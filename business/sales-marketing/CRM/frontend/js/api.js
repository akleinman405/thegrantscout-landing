// API wrapper for Supabase
// Uses fetch directly instead of supabase-js for smaller bundle size

const API = {
    baseUrl: SUPABASE_URL,
    headers: {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    },

    // Generic request helper
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}/rest/v1/${endpoint}`;
        const response = await fetch(url, {
            headers: this.headers,
            ...options
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || `HTTP ${response.status}`);
        }

        // Handle empty responses (DELETE)
        const text = await response.text();
        return text ? JSON.parse(text) : null;
    },

    // === PROSPECTS ===

    async getProspects({ segment, status, limit = 50, offset = 0 } = {}) {
        let query = `prospects?order=created_at.desc&limit=${limit}&offset=${offset}`;
        if (segment && segment !== 'all') query += `&segment=eq.${segment}`;
        if (status && status !== 'all') query += `&status=eq.${status}`;
        return this.request(query);
    },

    async getCallQueue({ segment, limit = 50 } = {}) {
        let query = `v_call_queue?limit=${limit}`;
        if (segment && segment !== 'all') query += `&segment=eq.${segment}`;
        return this.request(query);
    },

    async getAllProspects({ limit = 500 } = {}) {
        // Get all prospects regardless of status
        return this.request(`prospects?order=org_name&limit=${limit}`);
    },

    async getAllProspectsWithLastCall({ limit = 2000, segment = null, calledOnly = false } = {}) {
        // Get prospects with their last call info via the view
        // Sort by call_count desc so called prospects appear first, then by last_call_date
        let query = `v_prospects_with_last_call?order=call_count.desc.nullslast,last_call_date.desc.nullslast,org_name&limit=${limit}`;
        if (segment && segment !== 'all') {
            query = `v_prospects_with_last_call?segment=eq.${segment}&order=call_count.desc.nullslast,last_call_date.desc.nullslast,org_name&limit=${limit}`;
        }
        if (calledOnly) {
            query = `v_prospects_with_last_call?call_count=gt.0&order=last_call_date.desc.nullslast,org_name&limit=${limit}`;
        }
        return this.request(query);
    },

    async getProspectsWithScheduledTasks({ limit = 500 } = {}) {
        // Get prospects that have pending tasks (scheduled calls)
        const tasks = await this.request(`tasks?completed=eq.false&select=prospect_id&order=due_date`);
        const prospectIds = [...new Set(tasks.map(t => t.prospect_id).filter(Boolean))];

        if (prospectIds.length === 0) return [];

        // Fetch those prospects from the view
        const idList = prospectIds.slice(0, limit).join(',');
        return this.request(`v_prospects_with_last_call?id=in.(${idList})&order=org_name`);
    },

    async getProspect(id) {
        const prospects = await this.request(`prospects?id=eq.${id}`);
        return prospects[0] || null;
    },

    async getProspectWithHistory(id) {
        const [prospect, calls, emails, tasks] = await Promise.all([
            this.getProspect(id),
            this.getCalls(id),
            this.getEmails(id),
            this.getTasks(id)
        ]);
        return { prospect, calls, emails, tasks };
    },

    async searchProspects(query, limit = 25) {
        // Search in org_name, contact_name, phone, ein
        const searchQuery = `prospects?or=(org_name.ilike.*${query}*,contact_name.ilike.*${query}*,phone.ilike.*${query}*,ein.ilike.*${query}*)&limit=${limit}`;
        return this.request(searchQuery);
    },

    async createProspect(data) {
        return this.request('prospects', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async updateProspect(id, data) {
        const result = await this.request(`prospects?id=eq.${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
        return result[0];
    },

    async deleteProspect(id) {
        return this.request(`prospects?id=eq.${id}`, {
            method: 'DELETE'
        });
    },

    // === CALLS ===

    async getCalls(prospectId) {
        return this.request(`calls?prospect_id=eq.${prospectId}&order=call_date.desc`);
    },

    async createCall(data) {
        return this.request('calls', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async updateCall(id, data) {
        const result = await this.request(`calls?id=eq.${id}`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
        return result[0];
    },

    async getFollowUps() {
        // Calls with follow_up_date <= today
        const today = new Date().toISOString().split('T')[0];
        return this.request(`calls?follow_up_date=lte.${today}&select=*,prospects(id,org_name,contact_name,phone,segment)&order=follow_up_date`);
    },

    // === EMAILS ===

    async getEmails(prospectId) {
        return this.request(`emails?prospect_id=eq.${prospectId}&order=sent_date.desc`);
    },

    async createEmail(data) {
        return this.request('emails', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // === TASKS ===

    async getTasks(prospectId) {
        return this.request(`tasks?prospect_id=eq.${prospectId}&order=due_date`);
    },

    async getTasksDue({ completed = false } = {}) {
        const today = new Date().toISOString().split('T')[0];
        return this.request(`v_todays_followups`);
    },

    async getAllPendingTasks() {
        return this.request(`tasks?completed=eq.false&order=due_date&select=*,prospects(id,org_name,contact_name,phone,segment)`);
    },

    async createTask(data) {
        return this.request('tasks', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async completeTask(id) {
        return this.request(`tasks?id=eq.${id}`, {
            method: 'PATCH',
            body: JSON.stringify({ completed: true })
        });
    },

    async deleteTask(id) {
        return this.request(`tasks?id=eq.${id}`, {
            method: 'DELETE'
        });
    },

    // === DAILY QUEUE ===

    async getDailyQueue({ date, segment } = {}) {
        // Get prospects with scheduled call tasks for a specific date
        const targetDate = date || new Date().toISOString().split('T')[0];
        let query = `v_daily_call_queue?scheduled_date=eq.${targetDate}`;
        if (segment && segment !== 'all') query += `&segment=eq.${segment}`;
        return this.request(query);
    },

    async getWeeklyQueue({ startDate, endDate, segment, callType } = {}) {
        // Get scheduled calls for a date range
        const start = startDate || new Date().toISOString().split('T')[0];
        const end = endDate || new Date(Date.now() + 7*24*60*60*1000).toISOString().split('T')[0];
        let query = `v_daily_call_queue?scheduled_date=gte.${start}&scheduled_date=lte.${end}`;
        if (segment && segment !== 'all') query += `&segment=eq.${segment}`;
        if (callType && callType !== 'all') query += `&call_type=eq.${callType}`;
        query += '&order=scheduled_date,tier.nullslast,icp_score.desc.nullslast';
        return this.request(query);
    },

    async rescheduleTask(taskId, newDate) {
        // Reschedule a task to a new date
        return this.request(`tasks?id=eq.${taskId}`, {
            method: 'PATCH',
            body: JSON.stringify({ due_date: newDate })
        });
    },

    async removeFromQueue(taskId) {
        // Remove a task from the queue (mark complete or delete)
        return this.request(`tasks?id=eq.${taskId}`, {
            method: 'DELETE'
        });
    },

    async getCalledToday() {
        // Get prospects that have been called today
        return this.request('v_called_today');
    },

    async scheduleCall(prospectId, date, description = null) {
        // Create a task to call this prospect on the given date
        return this.createTask({
            prospect_id: prospectId,
            due_date: date,
            type: 'call',
            description: description || 'Scheduled call'
        });
    },

    async getScheduledDates({ startDate, endDate } = {}) {
        // Get dates that have scheduled calls (for showing badges on date picker)
        const start = startDate || new Date().toISOString().split('T')[0];
        const end = endDate || new Date(Date.now() + 30*24*60*60*1000).toISOString().split('T')[0];
        return this.request(`tasks?type=eq.call&completed=eq.false&due_date=gte.${start}&due_date=lte.${end}&select=due_date`);
    },

    // === SOURCE LISTS ===

    async getSourceLists() {
        return this.request('source_lists?order=created_at.desc');
    },

    async createSourceList(data) {
        return this.request('source_lists', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    // === DASHBOARD ===

    async getDashboardStats() {
        const stats = await this.request('v_dashboard_stats');
        return stats[0] || {};
    },

    async getDashboardMetrics(days = 30, segment = null) {
        // Call the RPC function for conversion metrics
        const params = { p_days: days };
        if (segment) params.p_segment = segment;

        const result = await this.request('rpc/get_dashboard_metrics', {
            method: 'POST',
            body: JSON.stringify(params)
        });
        return result[0] || {};
    },

    async getRecentCalls(limit = 10) {
        return this.request(`calls?order=call_date.desc&limit=${limit}&select=*,prospects(id,org_name,segment)`);
    },

    // === BULK IMPORT ===

    async bulkCreateProspects(prospects) {
        // Supabase supports bulk insert
        return this.request('prospects', {
            method: 'POST',
            body: JSON.stringify(prospects)
        });
    },

    // === TIME TRACKING ===

    async clockIn(plannedHours = null, plannedCalls = null) {
        const data = {
            clock_in: new Date().toISOString()
        };
        if (plannedHours) data.planned_hours = plannedHours;
        if (plannedCalls) data.planned_calls = plannedCalls;

        const result = await this.request('work_sessions', {
            method: 'POST',
            body: JSON.stringify(data)
        });
        return result[0];
    },

    async clockOut(sessionId, notes = null) {
        const data = {
            clock_out: new Date().toISOString()
        };
        if (notes) data.notes = notes;

        const result = await this.request(`work_sessions?id=eq.${sessionId}`, {
            method: 'PATCH',
            body: JSON.stringify(data)
        });
        return result[0];
    },

    async getActiveSession() {
        const result = await this.request('v_active_session');
        return result[0] || null;
    },

    async getSessionStats(days = 7) {
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);
        return this.request(`v_work_session_stats?clock_in=gte.${startDate.toISOString()}&order=clock_in.desc`);
    },

    async updateCallSession(callId, sessionId) {
        return this.request(`calls?id=eq.${callId}`, {
            method: 'PATCH',
            body: JSON.stringify({ work_session_id: sessionId })
        });
    },

    // === CAMPAIGNS ===

    async getCampaignStats() {
        const stats = await this.request('v_campaign_stats');
        return stats[0] || {};
    },

    async getCampaignStatsByVertical() {
        return this.request('v_campaign_stats_by_vertical');
    },

    async getCampaignRecent(limit = 20) {
        return this.request(`v_campaign_recent?limit=${limit}`);
    },

    async getProspectCampaignEmails(prospectId) {
        return this.request(`campaign_emails?prospect_id=eq.${prospectId}&order=sent_at.desc`);
    },

    // === EMAIL CONVERSATIONS ===

    async getProspectConversations(prospectId) {
        return this.request(`email_conversations?prospect_id=eq.${prospectId}&order=sent_at.desc`);
    },

    async getProspectConversationsByEmail(email) {
        return this.request(`email_conversations?email_address=eq.${email.toLowerCase()}&order=sent_at.desc`);
    },

    async getConversationThread(threadId) {
        return this.request(`email_conversations?gmail_thread_id=eq.${threadId}&order=sent_at`);
    },

    async getProspectConversationSummary(prospectId) {
        const result = await this.request(`v_prospect_conversation_summary?prospect_id=eq.${prospectId}`);
        return result[0] || null;
    },

    async getRecentConversations(limit = 20) {
        return this.request(`v_recent_conversations?limit=${limit}`);
    },

    async updateConversationSentiment(conversationId, sentiment) {
        return this.request(`email_conversations?id=eq.${conversationId}`, {
            method: 'PATCH',
            body: JSON.stringify({ reply_sentiment: sentiment })
        });
    }
};
