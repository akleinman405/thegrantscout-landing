// Dashboard View
// Stats, conversion funnel, and activity overview

const DashboardView = {
    timePeriod: 'week', // 'today', 'week', 'month', 'last30'
    segment: 'all',     // 'all', 'nonprofit', 'foundation', 'foundation_mgmt'
    stats: {},
    metrics: {},
    recentCalls: [],
    weeklyData: { calls: {}, emails: {} },
    // Daily goals from January schedule
    dailyCallGoals: { Mon: 45, Tue: 30, Wed: 75, Thu: 30, Fri: 60 },
    dailyEmailGoal: 400,
    monthlyCallGoal: 1040, // ~240/week * 4.33 weeks
    monthlyEmailGoal: 8800, // 400/day * 22 workdays
    weekOffset: 0, // 0 = current week, -1 = last week, etc.
    viewMode: 'weekly', // 'weekly' or 'monthly'
    editMode: false, // true when editing goals inline

    async render() {
        const container = document.getElementById('app');
        container.innerHTML = `
            <div class="view-header">
                <h1>Dashboard</h1>
            </div>

            <!-- Weekly/Monthly Tracker -->
            <div class="card" id="weekly-tracker">
                <div class="weekly-tracker-header">
                    <div class="tracker-nav">
                        <button class="btn-icon" id="prev-period-btn" title="Previous">&larr;</button>
                        <h3 id="tracker-title" class="clickable-title">Weekly Progress</h3>
                        <button class="btn-icon" id="next-period-btn" title="Next">&rarr;</button>
                    </div>
                    <div id="edit-goals-container">
                        <button class="btn btn-small btn-secondary" id="edit-goals-btn">Edit Goals</button>
                        <button class="btn btn-small btn-primary hidden" id="save-goals-btn">Save</button>
                        <button class="btn btn-small btn-secondary hidden" id="cancel-goals-btn">Cancel</button>
                    </div>
                </div>
                <div id="weekly-tracker-content">
                    <div class="loading-inline">Loading...</div>
                </div>
            </div>

            <!-- Phone Funnel by Segment -->
            <div class="card mt-16">
                <h3>📞 Phone Pipeline</h3>
                <div id="phone-funnel">
                    <div class="loading-inline">Loading...</div>
                </div>
            </div>

            <!-- Email Funnel by Segment -->
            <div class="card mt-16">
                <h3>📧 Email Pipeline</h3>
                <div id="email-funnel">
                    <div class="loading-inline">Loading...</div>
                </div>
            </div>

            <!-- Recent Activity -->
            <div class="card mt-16">
                <h3>Recent Activity</h3>
                <div id="recent-activity">
                    <div class="loading-inline">Loading...</div>
                </div>
            </div>

            <!-- Admin -->
            <div class="card mt-16">
                <h3>Admin</h3>
                <div style="display: grid; gap: 8px; margin-top: 12px;">
                    <button class="btn btn-secondary btn-block" onclick="navigateTo('import')">
                        &#128228; Import Prospects
                    </button>
                </div>
            </div>
        `;

        this.attachHandlers();
        await this.loadData();
    },

    attachHandlers() {
        // Edit goals button - toggle edit mode
        document.getElementById('edit-goals-btn').addEventListener('click', () => {
            this.editMode = true;
            this.updateEditButtonsVisibility();
            if (this.viewMode === 'weekly') {
                this.renderWeeklyTracker();
            } else {
                this.renderMonthlyTracker();
            }
        });

        // Save goals button
        document.getElementById('save-goals-btn').addEventListener('click', () => {
            this.saveGoals();
        });

        // Cancel goals button
        document.getElementById('cancel-goals-btn').addEventListener('click', () => {
            this.editMode = false;
            this.updateEditButtonsVisibility();
            if (this.viewMode === 'weekly') {
                this.renderWeeklyTracker();
            } else {
                this.renderMonthlyTracker();
            }
        });

        // Previous period button
        document.getElementById('prev-period-btn').addEventListener('click', () => {
            this.weekOffset--;
            this.loadTrackerData();
        });

        // Next period button (allow future weeks for goal planning)
        document.getElementById('next-period-btn').addEventListener('click', () => {
            this.weekOffset++;
            this.loadTrackerData();
        });

        // Toggle weekly/monthly
        document.getElementById('tracker-title').addEventListener('click', () => {
            this.viewMode = this.viewMode === 'weekly' ? 'monthly' : 'weekly';
            this.weekOffset = 0; // Reset offset when switching
            this.editMode = false; // Exit edit mode when switching
            this.updateEditButtonsVisibility();
            this.loadTrackerData();
        });
    },

    updateEditButtonsVisibility() {
        const editBtn = document.getElementById('edit-goals-btn');
        const saveBtn = document.getElementById('save-goals-btn');
        const cancelBtn = document.getElementById('cancel-goals-btn');

        if (this.editMode) {
            editBtn.classList.add('hidden');
            saveBtn.classList.remove('hidden');
            cancelBtn.classList.remove('hidden');
        } else {
            editBtn.classList.remove('hidden');
            saveBtn.classList.add('hidden');
            cancelBtn.classList.add('hidden');
        }
    },

    saveGoals() {
        if (this.viewMode === 'weekly') {
            // Read values from inputs
            const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
            dayNames.forEach(day => {
                const input = document.querySelector(`input[data-day="${day}"]`);
                if (input) {
                    this.dailyCallGoals[day] = parseInt(input.value) || 0;
                }
            });
            const emailInput = document.querySelector('input[data-email-goal]');
            if (emailInput) {
                this.dailyEmailGoal = parseInt(emailInput.value) || 400;
            }
            // Save to localStorage
            localStorage.setItem('crm_daily_call_goals', JSON.stringify(this.dailyCallGoals));
            localStorage.setItem('crm_daily_email_goal', this.dailyEmailGoal);
        } else {
            // Monthly goals
            const callInput = document.querySelector('input[data-monthly-call-goal]');
            const emailInput = document.querySelector('input[data-monthly-email-goal]');
            if (callInput) this.monthlyCallGoal = parseInt(callInput.value) || 1040;
            if (emailInput) this.monthlyEmailGoal = parseInt(emailInput.value) || 8800;
            localStorage.setItem('crm_monthly_call_goal', this.monthlyCallGoal);
            localStorage.setItem('crm_monthly_email_goal', this.monthlyEmailGoal);
        }

        this.editMode = false;
        this.updateEditButtonsVisibility();
        if (this.viewMode === 'weekly') {
            this.renderWeeklyTracker();
        } else {
            this.renderMonthlyTracker();
        }
        showToast('Goals saved', 'success');
    },

    async loadTrackerData() {
        if (this.viewMode === 'weekly') {
            const weekDates = this.getWeekDates();
            const [weeklyCalls, weeklyEmails] = await Promise.all([
                this.fetchWeeklyCalls(weekDates),
                this.fetchWeeklyEmails(weekDates)
            ]);
            this.weeklyData = { calls: weeklyCalls, emails: weeklyEmails };
            this.renderWeeklyTracker();
        } else {
            const monthData = await this.fetchMonthlyData();
            this.monthlyData = monthData;
            this.renderMonthlyTracker();
        }
    },

    loadSavedGoals() {
        // Load goals from localStorage
        const savedCallGoals = localStorage.getItem('crm_daily_call_goals');
        if (savedCallGoals) {
            try {
                this.dailyCallGoals = JSON.parse(savedCallGoals);
            } catch (e) {}
        }
        const savedEmailGoal = localStorage.getItem('crm_daily_email_goal');
        if (savedEmailGoal) this.dailyEmailGoal = parseInt(savedEmailGoal);

        const savedMonthlyCallGoal = localStorage.getItem('crm_monthly_call_goal');
        if (savedMonthlyCallGoal) this.monthlyCallGoal = parseInt(savedMonthlyCallGoal);

        const savedMonthlyEmailGoal = localStorage.getItem('crm_monthly_email_goal');
        if (savedMonthlyEmailGoal) this.monthlyEmailGoal = parseInt(savedMonthlyEmailGoal);
    },

    async loadData() {
        this.loadSavedGoals();
        try {
            // Get week dates for weekly tracker
            const weekDates = this.getWeekDates();

            const [recentCalls, weeklyCalls, weeklyEmails, pipelineData] = await Promise.all([
                API.getRecentCalls(10),
                this.fetchWeeklyCalls(weekDates),
                this.fetchWeeklyEmails(weekDates),
                this.fetchPipelineBySegment()
            ]);

            this.recentCalls = recentCalls;
            this.weeklyData = { calls: weeklyCalls, emails: weeklyEmails };
            this.pipelineData = pipelineData;

            this.renderWeeklyTracker();
            this.renderPhoneFunnel();
            this.renderEmailFunnel();
            this.renderActivity();
        } catch (error) {
            console.error('Failed to load dashboard:', error);
            showToast('Failed to load dashboard', 'error');
        }
    },

    async fetchPipelineBySegment() {
        try {
            // Get prospect counts by segment and status
            const prospects = await API.request('v_prospects_with_last_call?select=segment,status,call_count');

            const segments = ['nonprofit', 'foundation', 'foundation_mgmt'];
            const result = {};

            segments.forEach(seg => {
                const segProspects = prospects.filter(p => p.segment === seg);
                result[seg] = {
                    total: segProspects.length,
                    called: segProspects.filter(p => p.call_count > 0).length,
                    contacted: segProspects.filter(p => p.status === 'contacted').length,
                    interested: segProspects.filter(p => p.status === 'interested').length,
                    converted: segProspects.filter(p => p.status === 'converted').length
                };
            });

            return result;
        } catch (e) {
            console.error('Failed to fetch pipeline:', e);
            return {};
        }
    },

    getWeekDates() {
        // Get Monday of current week, adjusted by weekOffset
        const today = new Date();
        const dayOfWeek = today.getDay();
        const monday = new Date(today);
        monday.setDate(today.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1));
        monday.setDate(monday.getDate() + (this.weekOffset * 7)); // Apply offset
        monday.setHours(0, 0, 0, 0);

        const dates = [];
        for (let i = 0; i < 5; i++) { // Mon-Fri
            const date = new Date(monday);
            date.setDate(monday.getDate() + i);
            dates.push(date.toISOString().split('T')[0]);
        }
        return dates;
    },

    getMonthDates() {
        // Get last 4 months including current, adjusted by offset (each offset = 4 months)
        const months = [];
        const today = new Date();
        const baseMonth = today.getMonth() + (this.weekOffset * 4);

        for (let i = 3; i >= 0; i--) {
            const d = new Date(today.getFullYear(), baseMonth - i, 1);
            months.push({
                year: d.getFullYear(),
                month: d.getMonth(),
                label: d.toLocaleDateString('en-US', { month: 'short' }),
                startDate: new Date(d.getFullYear(), d.getMonth(), 1).toISOString().split('T')[0],
                endDate: new Date(d.getFullYear(), d.getMonth() + 1, 0).toISOString().split('T')[0]
            });
        }
        return months;
    },

    async fetchMonthlyData() {
        const months = this.getMonthDates();
        const result = { calls: {}, emails: {} };

        for (const m of months) {
            try {
                const [calls, manualEmails, campaignEmails] = await Promise.all([
                    API.request(`calls?call_date=gte.${m.startDate}&call_date=lte.${m.endDate}&select=id`),
                    API.request(`emails?sent_date=gte.${m.startDate}&sent_date=lte.${m.endDate}&select=id`),
                    API.request(`campaign_emails?sent_at=gte.${m.startDate}&sent_at=lte.${m.endDate}&status=eq.SUCCESS&select=id`)
                ]);
                result.calls[m.label] = calls.length;
                result.emails[m.label] = manualEmails.length + campaignEmails.length;
            } catch (e) {
                result.calls[m.label] = 0;
                result.emails[m.label] = 0;
            }
        }

        return result;
    },

    renderMonthlyTracker() {
        const container = document.getElementById('weekly-tracker-content');
        const titleEl = document.getElementById('tracker-title');
        const months = this.getMonthDates();
        const today = new Date();

        // Update title
        titleEl.textContent = 'Monthly Progress';

        // Use stored monthly goals
        const monthlyCallGoal = this.monthlyCallGoal;
        const monthlyEmailGoal = this.monthlyEmailGoal;

        // Calculate totals and goals
        let totalCalls = 0, totalEmails = 0;
        let totalCallGoal = 0, totalEmailGoal = 0;

        months.forEach(m => {
            totalCalls += this.monthlyData.calls[m.label] || 0;
            totalEmails += this.monthlyData.emails[m.label] || 0;
            // Only count goals for months up to current month
            const monthEnd = new Date(m.endDate);
            if (monthEnd <= today || m.month === today.getMonth()) {
                totalCallGoal += monthlyCallGoal;
                totalEmailGoal += monthlyEmailGoal;
            }
        });

        container.innerHTML = `
            <table class="weekly-table">
                <thead>
                    <tr>
                        <th></th>
                        ${months.map(m => `<th>${m.label}</th>`).join('')}
                        <th class="total-col">Total</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="calls-row">
                        <td class="row-label">📞 Calls</td>
                        ${months.map((m, i) => {
                            const actual = this.monthlyData.calls[m.label] || 0;
                            const isCurrent = m.month === today.getMonth() && m.year === today.getFullYear();
                            const isPast = new Date(m.endDate) < today && !isCurrent;
                            const metGoal = actual >= monthlyCallGoal;
                            const cellClass = isPast ? (metGoal ? 'goal-met' : 'goal-missed') : (isCurrent ? 'today-col' : '');
                            if (this.editMode && i === 0) {
                                return `<td class="${cellClass}"><span class="actual">${actual}</span>/<input type="number" class="goal-input" data-monthly-call-goal value="${monthlyCallGoal}" min="0"></td>`;
                            }
                            return `<td class="${cellClass}"><span class="actual">${actual}</span><span class="goal">/${monthlyCallGoal}</span></td>`;
                        }).join('')}
                        <td class="total-col"><span class="actual">${totalCalls}</span><span class="goal">/${totalCallGoal}</span></td>
                    </tr>
                    <tr class="emails-row">
                        <td class="row-label">📧 Emails</td>
                        ${months.map((m, i) => {
                            const actual = this.monthlyData.emails[m.label] || 0;
                            const isCurrent = m.month === today.getMonth() && m.year === today.getFullYear();
                            const isPast = new Date(m.endDate) < today && !isCurrent;
                            const metGoal = actual >= monthlyEmailGoal;
                            const cellClass = isPast ? (metGoal ? 'goal-met' : 'goal-missed') : (isCurrent ? 'today-col' : '');
                            if (this.editMode && i === 0) {
                                return `<td class="${cellClass}"><span class="actual">${actual}</span>/<input type="number" class="goal-input" data-monthly-email-goal value="${monthlyEmailGoal}" min="0"></td>`;
                            }
                            return `<td class="${cellClass}"><span class="actual">${actual}</span><span class="goal">/${monthlyEmailGoal}</span></td>`;
                        }).join('')}
                        <td class="total-col"><span class="actual">${totalEmails}</span><span class="goal">/${totalEmailGoal}</span></td>
                    </tr>
                </tbody>
            </table>
        `;
    },

    async fetchWeeklyCalls(dates) {
        const startDate = dates[0];
        const endDate = dates[dates.length - 1];
        try {
            const calls = await API.request(`calls?call_date=gte.${startDate}&call_date=lte.${endDate}&select=id,call_date`);
            // Group by date
            const byDate = {};
            dates.forEach(d => byDate[d] = 0);
            calls.forEach(c => {
                const d = c.call_date?.split('T')[0];
                if (d && byDate.hasOwnProperty(d)) byDate[d]++;
            });
            return byDate;
        } catch (e) {
            console.error('Failed to fetch weekly calls:', e);
            return {};
        }
    },

    async fetchWeeklyEmails(dates) {
        const startDate = dates[0];
        const endDate = dates[dates.length - 1];
        try {
            // Count both manual emails AND campaign emails sent (SUCCESS status)
            const [manualEmails, campaignEmails] = await Promise.all([
                API.request(`emails?sent_date=gte.${startDate}&sent_date=lte.${endDate}&select=id,sent_date`),
                API.request(`campaign_emails?sent_at=gte.${startDate}&sent_at=lte.${endDate}&status=eq.SUCCESS&select=id,sent_at`)
            ]);

            // Group by date
            const byDate = {};
            dates.forEach(d => byDate[d] = 0);

            // Count manual emails
            manualEmails.forEach(e => {
                const d = e.sent_date?.split('T')[0];
                if (d && byDate.hasOwnProperty(d)) byDate[d]++;
            });

            // Count campaign emails
            campaignEmails.forEach(e => {
                const d = e.sent_at?.split('T')[0];
                if (d && byDate.hasOwnProperty(d)) byDate[d]++;
            });

            return byDate;
        } catch (e) {
            console.error('Failed to fetch weekly emails:', e);
            return {};
        }
    },

    renderWeeklyTracker() {
        const container = document.getElementById('weekly-tracker-content');
        const titleEl = document.getElementById('tracker-title');
        const dates = this.getWeekDates();
        const dayNames = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
        const today = new Date().toISOString().split('T')[0];

        // Update title with week range
        const startDate = new Date(dates[0] + 'T12:00:00');
        const endDate = new Date(dates[4] + 'T12:00:00');
        const weekLabel = this.weekOffset === 0 ? 'This Week' :
                          this.weekOffset === -1 ? 'Last Week' :
                          `${startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${endDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
        titleEl.textContent = `Weekly: ${weekLabel}`;

        // Calculate totals with day-specific call goals
        let totalCalls = 0, totalEmails = 0;
        let callGoalTotal = 0, emailGoalTotal = 0;
        dates.forEach((d, i) => {
            totalCalls += this.weeklyData.calls[d] || 0;
            totalEmails += this.weeklyData.emails[d] || 0;
            // Only count goals for days up to today
            if (d <= today) {
                callGoalTotal += this.dailyCallGoals[dayNames[i]] || 0;
                emailGoalTotal += this.dailyEmailGoal;
            }
        });

        container.innerHTML = `
            <table class="weekly-table">
                <thead>
                    <tr>
                        <th></th>
                        ${dates.map((d, i) => {
                            const date = new Date(d + 'T12:00:00');
                            const month = date.getMonth() + 1;
                            const day = date.getDate();
                            const isToday = d === today;
                            return `<th class="${isToday ? 'today-col' : ''}">${dayNames[i]}<br><span class="date-label">${month}/${day}</span></th>`;
                        }).join('')}
                        <th class="total-col">Total</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="calls-row">
                        <td class="row-label">📞 Calls</td>
                        ${dates.map((d, i) => {
                            const actual = this.weeklyData.calls[d] || 0;
                            const goal = this.dailyCallGoals[dayNames[i]] || 0;
                            const isToday = d === today;
                            const isPast = d < today;
                            const metGoal = actual >= goal;
                            const cellClass = isPast ? (metGoal ? 'goal-met' : 'goal-missed') : (isToday ? 'today-col' : '');
                            if (this.editMode) {
                                return `<td class="${cellClass}"><span class="actual">${actual}</span>/<input type="number" class="goal-input" data-day="${dayNames[i]}" value="${goal}" min="0"></td>`;
                            }
                            return `<td class="${cellClass}"><span class="actual">${actual}</span><span class="goal">/${goal}</span></td>`;
                        }).join('')}
                        <td class="total-col ${totalCalls >= callGoalTotal ? 'goal-met' : ''}"><span class="actual">${totalCalls}</span><span class="goal">/${callGoalTotal}</span></td>
                    </tr>
                    <tr class="emails-row">
                        <td class="row-label">📧 Emails</td>
                        ${dates.map((d, i) => {
                            const actual = this.weeklyData.emails[d] || 0;
                            const goal = this.dailyEmailGoal;
                            const isToday = d === today;
                            const isPast = d < today;
                            const metGoal = actual >= goal;
                            const cellClass = isPast ? (metGoal ? 'goal-met' : 'goal-missed') : (isToday ? 'today-col' : '');
                            // Only show email goal input on first column (same goal for all days)
                            if (this.editMode && i === 0) {
                                return `<td class="${cellClass}"><span class="actual">${actual}</span>/<input type="number" class="goal-input" data-email-goal value="${goal}" min="0"></td>`;
                            }
                            return `<td class="${cellClass}"><span class="actual">${actual}</span><span class="goal">/${goal}</span></td>`;
                        }).join('')}
                        <td class="total-col ${totalEmails >= emailGoalTotal ? 'goal-met' : ''}"><span class="actual">${totalEmails}</span><span class="goal">/${emailGoalTotal}</span></td>
                    </tr>
                </tbody>
            </table>
        `;
    },

    renderPhoneFunnel() {
        const container = document.getElementById('phone-funnel');
        const data = this.pipelineData || {};

        const segments = [
            { key: 'nonprofit', label: 'Nonprofits', color: '#3b82f6' },
            { key: 'foundation', label: 'Foundations', color: '#8b5cf6' },
            { key: 'foundation_mgmt', label: 'Fdn Mgmt', color: '#f59e0b' }
        ];

        container.innerHTML = `
            <div class="horizontal-funnel">
                <div class="funnel-header-row">
                    <div class="funnel-segment-label"></div>
                    <div class="funnel-stage-header">Total</div>
                    <div class="funnel-stage-header">Called</div>
                    <div class="funnel-stage-header">Contacted</div>
                    <div class="funnel-stage-header">Interested</div>
                    <div class="funnel-stage-header">Converted</div>
                </div>
                ${segments.map(seg => {
                    const d = data[seg.key] || {};
                    return `
                        <div class="funnel-row">
                            <div class="funnel-segment-label" style="color: ${seg.color}">${seg.label}</div>
                            <div class="funnel-cell">${d.total || 0}</div>
                            <div class="funnel-cell">${d.called || 0}</div>
                            <div class="funnel-cell">${d.contacted || 0}</div>
                            <div class="funnel-cell">${d.interested || 0}</div>
                            <div class="funnel-cell funnel-converted">${d.converted || 0}</div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    },

    renderEmailFunnel() {
        const container = document.getElementById('email-funnel');

        // Show email stats by segment
        this.fetchEmailStatsBySegment().then(stats => {
            container.innerHTML = `
                <div class="horizontal-funnel">
                    <div class="funnel-header-row">
                        <div class="funnel-segment-label"></div>
                        <div class="funnel-stage-header">Sent</div>
                        <div class="funnel-stage-header">Bounced</div>
                        <div class="funnel-stage-header">Delivered</div>
                    </div>
                    ${stats.map(s => `
                        <div class="funnel-row">
                            <div class="funnel-segment-label" style="color: ${s.color}">${s.label}</div>
                            <div class="funnel-cell">${s.sent}</div>
                            <div class="funnel-cell">${s.bounced}</div>
                            <div class="funnel-cell funnel-converted">${s.delivered}</div>
                        </div>
                    `).join('')}
                </div>
                <p class="text-muted text-small mt-8">By campaign vertical. Link prospect_id to show by segment.</p>
            `;
        });
    },

    async fetchEmailStatsBySegment() {
        try {
            // Get campaign emails - grouped by vertical (prospect_id not linked yet)
            const campaignEmails = await API.request('campaign_emails?select=id,status,vertical');

            // Group by vertical since segment requires prospect_id to be linked
            const verticals = [
                { key: 'debarment', label: 'Debarment', color: '#ef4444' },
                { key: 'food_recall', label: 'Food Recall', color: '#f59e0b' },
                { key: 'grant_alerts', label: 'Grants', color: '#3b82f6' }
            ];

            return verticals.map(v => {
                const vEmails = campaignEmails.filter(e => e.vertical === v.key);
                const sent = vEmails.length;
                const bounced = vEmails.filter(e => e.status === 'BOUNCED').length;
                const delivered = vEmails.filter(e => e.status === 'SUCCESS').length;

                return {
                    label: v.label,
                    color: v.color,
                    sent,
                    bounced,
                    delivered
                };
            });
        } catch (e) {
            console.error('Failed to fetch email stats:', e);
            return [];
        }
    },

    renderActivity() {
        const container = document.getElementById('recent-activity');

        if (this.recentCalls.length === 0) {
            container.innerHTML = `<p class="text-muted text-center">No recent activity</p>`;
            return;
        }

        container.innerHTML = this.recentCalls.map(call => {
            const prospect = call.prospects || {};
            const outcomeIcons = {
                'vm_left': '&#128172;',
                'talked_to_someone': '&#128483;',
                'reached_decision_maker': '&#11088;',
                'no_answer': '&#128276;',
                'wrong_number': '&#128683;',
                'sent_email_request': '&#128231;',
                'disconnected': '&#128274;'
            };

            return `
                <div class="activity-item">
                    <div class="activity-icon">${outcomeIcons[call.outcome] || '&#128222;'}</div>
                    <div class="activity-content">
                        <div class="activity-title">
                            <a href="#" onclick="showProspectDetail(${call.prospect_id}); return false;"
                               style="color: var(--primary); text-decoration: none;">
                                ${escapeHtml(prospect.org_name || 'Unknown')}
                            </a>
                        </div>
                        <div class="activity-meta">
                            ${formatOutcome(call.outcome)}
                            ${call.interest ? ' - ' + call.interest : ''}
                            &middot; ${formatTimeAgo(call.call_date)}
                        </div>
                        ${call.notes ? `<div style="font-size: 0.875rem; margin-top: 4px;">${escapeHtml(call.notes.substring(0, 100))}${call.notes.length > 100 ? '...' : ''}</div>` : ''}
                    </div>
                </div>
            `;
        }).join('');
    }
};

function formatOutcome(outcome) {
    const labels = {
        'vm_left': 'Left voicemail',
        'talked_to_someone': 'Talked to someone',
        'reached_decision_maker': 'Reached decision maker',
        'no_answer': 'No answer',
        'wrong_number': 'Wrong number',
        'sent_email_request': 'Sent email request',
        'disconnected': 'Disconnected'
    };
    return labels[outcome] || outcome;
}

function formatTimeAgo(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}
