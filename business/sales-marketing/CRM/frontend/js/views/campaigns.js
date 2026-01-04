// Campaigns View - Grant Scout Email Campaign Stats & Activity
// Shows email campaign performance and recent activity

const CampaignsView = {
    stats: null,
    recentActivity: [],

    async render() {
        const container = document.getElementById('app');

        container.innerHTML = `
            <div class="view-header">
                <h1>Email Campaigns</h1>
                <button class="btn btn-secondary btn-small" id="refresh-campaigns">
                    Refresh
                </button>
            </div>

            <div id="campaigns-content">
                <div class="text-center" style="padding: 40px;">
                    <div class="spinner"></div>
                    <p class="text-muted" style="margin-top: 12px;">Loading campaign data...</p>
                </div>
            </div>
        `;

        document.getElementById('refresh-campaigns').addEventListener('click', () => this.loadData());

        await this.loadData();
    },

    async loadData() {
        try {
            const [stats, recentActivity] = await Promise.all([
                API.getCampaignStats(),
                API.getCampaignRecent(20)
            ]);

            this.stats = stats;
            this.recentActivity = recentActivity || [];

            this.renderContent();
        } catch (error) {
            console.error('Failed to load campaign data:', error);
            document.getElementById('campaigns-content').innerHTML = `
                <div class="card">
                    <p class="text-danger">Failed to load campaign data</p>
                    <button class="btn btn-primary mt-16" onclick="CampaignsView.loadData()">Retry</button>
                </div>
            `;
        }
    },

    renderContent() {
        const content = document.getElementById('campaigns-content');
        const s = this.stats;

        // Calculate reply rate
        const replyRate = s.total_replies && s.sent_success
            ? Math.round((s.total_replies / s.sent_success) * 100 * 10) / 10
            : 0;

        content.innerHTML = `
            <!-- Overall Stats -->
            <div class="card">
                <h3>Grant Scout Campaign</h3>
                <div class="stats-grid" style="margin-top: 16px;">
                    <div class="stat-item">
                        <div class="stat-value">${this.formatNumber(s.sent_success)}</div>
                        <div class="stat-label">Sent</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${this.formatNumber(s.unique_recipients)}</div>
                        <div class="stat-label">Recipients</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${s.bounce_rate || 0}%</div>
                        <div class="stat-label">Bounce Rate</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${this.formatNumber(s.total_replies || 0)}</div>
                        <div class="stat-label">Replies</div>
                    </div>
                </div>
            </div>

            <!-- Message Type Breakdown -->
            <div class="card mt-16">
                <h3>Message Types</h3>
                <div class="progress-container" style="margin-top: 16px;">
                    <div class="progress-bar">
                        <div class="progress-fill progress-initial" style="width: ${this.getPercent(s.initial_sent, s.sent_success)}%"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 0.875rem;">
                        <span><span class="dot dot-initial"></span> Initial: ${this.formatNumber(s.initial_sent)}</span>
                        <span><span class="dot dot-followup"></span> Follow-up: ${this.formatNumber(s.followup_sent)}</span>
                    </div>
                </div>
            </div>

            <!-- Reply Sentiment -->
            <div class="card mt-16">
                <h3>Reply Breakdown</h3>
                <table style="width: 100%; font-size: 0.875rem; margin-top: 12px;">
                    <tr>
                        <td class="text-muted">Total Replies</td>
                        <td><strong>${this.formatNumber(s.total_replies || 0)}</strong> (${replyRate}% reply rate)</td>
                    </tr>
                    <tr>
                        <td><span style="color: var(--success);">&#10003;</span> Interested</td>
                        <td><strong>${this.formatNumber(s.replies_interested || 0)}</strong></td>
                    </tr>
                    <tr>
                        <td><span style="color: var(--danger);">&#10007;</span> Not Interested</td>
                        <td><strong>${this.formatNumber(s.replies_not_interested || 0)}</strong></td>
                    </tr>
                    <tr>
                        <td><span style="color: var(--warning);">&#63;</span> Questions</td>
                        <td><strong>${this.formatNumber(s.replies_questions || 0)}</strong></td>
                    </tr>
                    <tr>
                        <td><span style="color: var(--primary);">&#128197;</span> Meeting Requested</td>
                        <td><strong>${this.formatNumber(s.replies_meeting || 0)}</strong></td>
                    </tr>
                </table>
                <p class="text-muted" style="margin-top: 12px; font-size: 0.75rem;">
                    Classify replies in the prospect detail view to track sentiment.
                </p>
            </div>

            <!-- Linked to CRM -->
            <div class="card mt-16">
                <h3>Activity</h3>
                <table style="width: 100%; font-size: 0.875rem; margin-top: 12px;">
                    <tr>
                        <td class="text-muted">Linked Prospects</td>
                        <td><strong>${this.formatNumber(s.linked_prospects)}</strong> / ${this.formatNumber(s.unique_recipients)}</td>
                    </tr>
                    <tr>
                        <td class="text-muted">Link Rate</td>
                        <td><strong>${this.getPercent(s.linked_prospects, s.unique_recipients)}%</strong></td>
                    </tr>
                    <tr>
                        <td class="text-muted">Sent Last 30 Days</td>
                        <td><strong>${this.formatNumber(s.sent_last_30_days)}</strong></td>
                    </tr>
                    <tr>
                        <td class="text-muted">Sent Last 7 Days</td>
                        <td><strong>${this.formatNumber(s.sent_last_7_days)}</strong></td>
                    </tr>
                </table>
            </div>

            <!-- Recent Activity -->
            <div class="card mt-16">
                <h3>Recent Sends</h3>
                ${this.recentActivity.length === 0
                    ? '<p class="text-muted" style="margin-top: 12px;">No recent activity</p>'
                    : `<div class="activity-list" style="margin-top: 12px;">
                        ${this.recentActivity.slice(0, 10).map(a => this.renderActivityItem(a)).join('')}
                    </div>`
                }
            </div>

            <!-- Sync Info -->
            <div class="card mt-16" style="background: var(--gray-50);">
                <h3>Sync Status</h3>
                <p class="text-muted" style="margin-top: 8px; font-size: 0.875rem;">
                    Campaign data synced from sent_tracker.csv.<br>
                    Run <code>python sync_campaign_emails.py</code> to update.
                </p>
            </div>
        `;

        // Add click handlers for activity items
        content.querySelectorAll('.activity-item[data-prospect-id]').forEach(item => {
            item.addEventListener('click', () => {
                const prospectId = item.dataset.prospectId;
                if (prospectId && prospectId !== 'null') {
                    showProspectDetail(prospectId);
                }
            });
        });
    },

    renderActivityItem(a) {
        const statusIcon = {
            'SUCCESS': '&#9989;',
            'BOUNCED': '&#10060;',
            'FAILED': '&#9888;'
        }[a.status] || '&#128231;';

        const hasProspect = a.prospect_id && a.prospect_org_name;
        const orgName = hasProspect ? a.prospect_org_name : a.email_address;

        return `
            <div class="activity-item ${hasProspect ? 'clickable' : ''}"
                 ${hasProspect ? `data-prospect-id="${a.prospect_id}"` : ''}>
                <div class="activity-icon">${statusIcon}</div>
                <div class="activity-content">
                    <div class="activity-title">${escapeHtml(orgName.substring(0, 35))}${orgName.length > 35 ? '...' : ''}</div>
                    <div class="activity-meta">
                        ${a.message_type === 'initial' ? 'Initial' : 'Follow-up'} &middot;
                        ${this.formatDate(a.sent_at)}
                    </div>
                </div>
                <span class="badge badge-${a.status.toLowerCase()}">${a.status}</span>
            </div>
        `;
    },

    formatNumber(n) {
        if (n === null || n === undefined) return '0';
        return n.toLocaleString();
    },

    getPercent(part, total) {
        if (!total || total === 0) return 0;
        return Math.round((part / total) * 100);
    },

    formatDate(dateStr) {
        if (!dateStr) return '';
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
};
