// Call Queue View - Day-by-Day Cold Calling Queue
// Shows scheduled calls organized by day with First Contact / Follow-up filtering

const QueueView = {
    // Filter state
    daysToShow: parseInt(localStorage.getItem('crm_queueDays')) || 7,
    callType: localStorage.getItem('crm_callType') || 'first_contact',
    segment: localStorage.getItem('crm_queueSegment') || 'all',

    // Data
    scheduledCalls: [],
    callsByDate: {},

    async render() {
        const container = document.getElementById('app');

        container.innerHTML = `
            <div class="view-header">
                <h1>Call Queue</h1>
                <span class="text-muted" id="queue-count">Loading...</span>
            </div>

            <!-- Filter Controls -->
            <div class="queue-filters">
                <div class="filter-group">
                    <label>Days</label>
                    <select id="days-filter" class="form-select form-select-small">
                        <option value="1" ${this.daysToShow === 1 ? 'selected' : ''}>Today Only</option>
                        <option value="7" ${this.daysToShow === 7 ? 'selected' : ''}>7 Days</option>
                        <option value="30" ${this.daysToShow === 30 ? 'selected' : ''}>30 Days</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Type</label>
                    <select id="type-filter" class="form-select form-select-small">
                        <option value="first_contact" ${this.callType === 'first_contact' ? 'selected' : ''}>First Contact</option>
                        <option value="follow_up" ${this.callType === 'follow_up' ? 'selected' : ''}>Follow-up</option>
                        <option value="all" ${this.callType === 'all' ? 'selected' : ''}>All Types</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>Segment</label>
                    <select id="segment-filter" class="form-select form-select-small">
                        <option value="all" ${this.segment === 'all' ? 'selected' : ''}>All Segments</option>
                        <option value="nonprofit" ${this.segment === 'nonprofit' ? 'selected' : ''}>Nonprofits</option>
                        <option value="foundation" ${this.segment === 'foundation' ? 'selected' : ''}>Foundations</option>
                        <option value="foundation_mgmt" ${this.segment === 'foundation_mgmt' ? 'selected' : ''}>Fdn Mgmt</option>
                    </select>
                </div>
            </div>

            <!-- Day-by-Day Queue -->
            <div id="queue-list">
                <div class="loading-inline">Loading...</div>
            </div>

            <!-- Reschedule Modal -->
            <div id="reschedule-modal" class="modal" style="display: none;">
                <div class="modal-content modal-small">
                    <div class="modal-header">
                        <h2>Reschedule Call</h2>
                        <button class="modal-close" onclick="closeModal('reschedule-modal')">&times;</button>
                    </div>
                    <div class="modal-body">
                        <p id="reschedule-prospect-name"></p>
                        <label>New Date:</label>
                        <input type="date" id="reschedule-date" class="form-input">
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="closeModal('reschedule-modal')">Cancel</button>
                        <button class="btn btn-primary" id="reschedule-save">Save</button>
                    </div>
                </div>
            </div>
        `;

        this.attachHandlers();
        await this.loadData();
    },

    attachHandlers() {
        // Days filter
        document.getElementById('days-filter').addEventListener('change', (e) => {
            this.daysToShow = parseInt(e.target.value);
            localStorage.setItem('crm_queueDays', this.daysToShow);
            this.loadData();
        });

        // Type filter
        document.getElementById('type-filter').addEventListener('change', (e) => {
            this.callType = e.target.value;
            localStorage.setItem('crm_callType', this.callType);
            this.loadData();
        });

        // Segment filter
        document.getElementById('segment-filter').addEventListener('change', (e) => {
            this.segment = e.target.value;
            localStorage.setItem('crm_queueSegment', this.segment);
            this.loadData();
        });
    },

    async loadData() {
        try {
            const today = new Date();
            const endDate = new Date(today);
            endDate.setDate(endDate.getDate() + this.daysToShow);

            this.scheduledCalls = await API.getWeeklyQueue({
                startDate: today.toISOString().split('T')[0],
                endDate: endDate.toISOString().split('T')[0],
                segment: this.segment,
                callType: this.callType
            });

            // Group by date
            this.groupByDate();
            this.renderQueue();
            this.updateCount();
        } catch (error) {
            console.error('Failed to load queue:', error);
            showToast('Failed to load queue', 'error');
        }
    },

    groupByDate() {
        this.callsByDate = {};

        // Create entries for all weekdays in range
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        for (let i = 0; i < this.daysToShow; i++) {
            const date = new Date(today);
            date.setDate(date.getDate() + i);

            // Skip weekends
            const dayOfWeek = date.getDay();
            if (dayOfWeek === 0 || dayOfWeek === 6) continue;

            const dateStr = date.toISOString().split('T')[0];
            this.callsByDate[dateStr] = [];
        }

        // Add calls to their dates
        for (const call of this.scheduledCalls) {
            const dateStr = call.scheduled_date;
            if (this.callsByDate[dateStr]) {
                this.callsByDate[dateStr].push(call);
            }
        }
    },

    updateCount() {
        const total = this.scheduledCalls.length;
        const typeLabel = this.callType === 'first_contact' ? 'first contact' :
                         this.callType === 'follow_up' ? 'follow-up' : '';
        document.getElementById('queue-count').textContent =
            `${total} ${typeLabel} call${total !== 1 ? 's' : ''} scheduled`;
    },

    renderQueue() {
        const listEl = document.getElementById('queue-list');
        const dates = Object.keys(this.callsByDate).sort();

        if (dates.length === 0) {
            listEl.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">&#128222;</div>
                    <div class="empty-state-title">No Calls Scheduled</div>
                    <p>Schedule prospects from the All Prospects view.</p>
                </div>
            `;
            return;
        }

        let html = '';
        for (const dateStr of dates) {
            const calls = this.callsByDate[dateStr];
            html += this.renderDaySection(dateStr, calls);
        }

        listEl.innerHTML = html;
        this.attachCardHandlers();
    },

    renderDaySection(dateStr, calls) {
        const dateLabel = this.formatDateHeader(dateStr);
        const count = calls.length;
        const isToday = dateStr === new Date().toISOString().split('T')[0];
        const today = new Date().toISOString().split('T')[0];

        return `
            <div class="queue-day ${isToday ? 'queue-day-today' : ''}" data-date="${dateStr}">
                <div class="queue-day-header">
                    <span class="queue-day-label">${dateLabel}</span>
                    <div class="queue-day-actions">
                        <input type="date" class="date-picker-inline" data-date="${dateStr}" min="${today}" value="${dateStr}" title="Move all calls to another day">
                        <span class="queue-day-count">${count} prospect${count !== 1 ? 's' : ''}</span>
                    </div>
                </div>
                <div class="queue-day-list">
                    ${count === 0
                        ? '<div class="queue-empty-day">No calls scheduled</div>'
                        : calls.map((call, index) => this.renderQueueCard(call, index + 1)).join('')
                    }
                </div>
            </div>
        `;
    },

    renderQueueCard(prospect, number) {
        const tierBadge = prospect.tier ? `<span class="badge">T${prospect.tier}</span>` : '';
        const stateBadge = prospect.state ? `<span class="badge badge-state">${prospect.state}</span>` : '';
        const icpBadge = prospect.icp_score ? `<span class="badge">ICP ${prospect.icp_score}</span>` : '';

        return `
            <div class="queue-card" data-id="${prospect.id}" data-task-id="${prospect.task_id}">
                <div class="queue-card-number">${number}</div>
                <div class="queue-card-content">
                    <div class="queue-card-header">
                        <div class="queue-card-title">${escapeHtml(prospect.org_name)}</div>
                        <div class="queue-card-actions">
                            <button class="btn-icon btn-reschedule" data-id="${prospect.id}" data-task-id="${prospect.task_id}" data-name="${escapeHtml(prospect.org_name)}" title="Reschedule">
                                &#128197;
                            </button>
                            <button class="btn-icon btn-remove" data-task-id="${prospect.task_id}" data-name="${escapeHtml(prospect.org_name)}" title="Remove from queue">
                                &#10005;
                            </button>
                        </div>
                    </div>
                    ${prospect.contact_name ? `<div class="queue-card-contact">Ask for: ${escapeHtml(prospect.contact_name)}${prospect.contact_title ? ' (' + escapeHtml(prospect.contact_title) + ')' : ''}</div>` : ''}
                    <div class="queue-card-phone">
                        <a href="tel:${prospect.phone}" onclick="event.stopPropagation()">&#128222; ${formatPhone(prospect.phone)}</a>
                    </div>
                    <div class="queue-card-badges">
                        <span class="badge badge-${prospect.segment}">${formatSegment(prospect.segment)}</span>
                        ${stateBadge}
                        ${tierBadge}
                        ${icpBadge}
                    </div>
                    ${prospect.pitch_angle ? `<div class="queue-card-pitch"><strong>Angle:</strong> ${escapeHtml(prospect.pitch_angle)}</div>` : ''}
                </div>
                <div class="queue-card-action-btn">
                    <button class="btn btn-primary btn-small btn-log-call" data-id="${prospect.id}" data-task-id="${prospect.task_id}">
                        Log Call
                    </button>
                </div>
            </div>
        `;
    },

    attachCardHandlers() {
        const container = document.getElementById('queue-list');

        // Inline date picker change -> move all calls to new date
        container.querySelectorAll('.date-picker-inline').forEach(picker => {
            picker.addEventListener('change', async (e) => {
                const fromDate = picker.dataset.date;
                const toDate = e.target.value;
                if (fromDate === toDate) return;

                const calls = this.callsByDate[fromDate] || [];
                if (calls.length === 0) {
                    showToast('No calls to move', 'info');
                    picker.value = fromDate;
                    return;
                }

                try {
                    for (const call of calls) {
                        await API.rescheduleTask(call.task_id, toDate);
                    }
                    showToast(`Moved ${calls.length} call${calls.length !== 1 ? 's' : ''} to ${toDate}`, 'success');
                    this.loadData();
                } catch (error) {
                    console.error('Failed to move calls:', error);
                    showToast('Failed to move calls', 'error');
                    picker.value = fromDate;
                }
            });
        });

        // Card click -> show prospect detail with queue context for navigation
        container.querySelectorAll('.queue-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (e.target.closest('button') || e.target.closest('a')) return;
                // Pass the full queue list and current index for prev/next navigation
                const allCalls = Object.values(this.callsByDate).flat();
                const currentIndex = allCalls.findIndex(c => String(c.id) === card.dataset.id);
                showProspectDetail(card.dataset.id, allCalls, currentIndex);
            });
        });

        // Log call button
        container.querySelectorAll('.btn-log-call').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                showLogCallModal(btn.dataset.id, btn.dataset.taskId);
            });
        });

        // Reschedule button
        container.querySelectorAll('.btn-reschedule').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.showRescheduleModal(btn.dataset.taskId, btn.dataset.name);
            });
        });

        // Remove button
        container.querySelectorAll('.btn-remove').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.removeFromQueue(btn.dataset.taskId, btn.dataset.name);
            });
        });
    },

    showRescheduleModal(taskId, prospectName) {
        document.getElementById('reschedule-prospect-name').textContent = prospectName;
        document.getElementById('reschedule-date').value = '';
        document.getElementById('reschedule-modal').style.display = 'flex';

        // Set min date to today
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('reschedule-date').min = today;

        // Save handler
        document.getElementById('reschedule-save').onclick = async () => {
            const newDate = document.getElementById('reschedule-date').value;
            if (!newDate) {
                showToast('Please select a date', 'error');
                return;
            }

            try {
                await API.rescheduleTask(taskId, newDate);
                closeModal('reschedule-modal');
                showToast('Call rescheduled', 'success');
                this.loadData();
            } catch (error) {
                console.error('Failed to reschedule:', error);
                showToast('Failed to reschedule', 'error');
            }
        };
    },

    async removeFromQueue(taskId, prospectName) {
        if (!confirm(`Remove "${prospectName}" from the queue?`)) return;

        try {
            await API.removeFromQueue(taskId);
            showToast('Removed from queue', 'success');
            this.loadData();
        } catch (error) {
            console.error('Failed to remove:', error);
            showToast('Failed to remove', 'error');
        }
    },

    showDateMoveModal(fromDate) {
        const calls = this.callsByDate[fromDate] || [];
        if (calls.length === 0) {
            showToast('No calls on this date to move', 'info');
            return;
        }

        const dateLabel = this.formatDateHeader(fromDate);
        document.getElementById('reschedule-prospect-name').textContent =
            `Move all ${calls.length} call${calls.length !== 1 ? 's' : ''} from ${dateLabel}`;
        document.getElementById('reschedule-date').value = '';
        document.getElementById('reschedule-modal').style.display = 'flex';

        // Set min date to today
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('reschedule-date').min = today;

        // Save handler - move all calls from this date
        document.getElementById('reschedule-save').onclick = async () => {
            const newDate = document.getElementById('reschedule-date').value;
            if (!newDate) {
                showToast('Please select a date', 'error');
                return;
            }

            try {
                // Move all calls from this date
                for (const call of calls) {
                    await API.rescheduleTask(call.task_id, newDate);
                }
                closeModal('reschedule-modal');
                showToast(`Moved ${calls.length} call${calls.length !== 1 ? 's' : ''} to new date`, 'success');
                this.loadData();
            } catch (error) {
                console.error('Failed to move calls:', error);
                showToast('Failed to move calls', 'error');
            }
        };
    },

    formatDateHeader(dateStr) {
        const date = new Date(dateStr + 'T12:00:00');
        const today = new Date();
        today.setHours(12, 0, 0, 0);
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);

        if (date.toDateString() === today.toDateString()) {
            return 'Today - ' + date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
        }
        if (date.toDateString() === tomorrow.toDateString()) {
            return 'Tomorrow - ' + date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
        }
        return date.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric' });
    }
};

// Helper functions
function formatPhone(phone) {
    if (!phone) return 'No phone';
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 10) {
        return `(${cleaned.slice(0,3)}) ${cleaned.slice(3,6)}-${cleaned.slice(6)}`;
    }
    if (cleaned.length === 11 && cleaned[0] === '1') {
        return `(${cleaned.slice(1,4)}) ${cleaned.slice(4,7)}-${cleaned.slice(7)}`;
    }
    return phone;
}

function formatSegment(segment) {
    const labels = {
        'nonprofit': 'Nonprofit',
        'foundation': 'Foundation',
        'foundation_mgmt': 'Fdn Mgmt'
    };
    return labels[segment] || segment;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
