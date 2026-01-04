// Schedule Call Modal
// Quick modal to assign a prospect to a specific call date

const ScheduleCallView = {
    prospectId: null,
    prospect: null,
    callback: null,

    async show(id, callback = null) {
        this.prospectId = id;
        this.callback = callback;
        const modal = document.getElementById('schedule-call-modal');
        const container = document.getElementById('schedule-call-form-container');

        container.innerHTML = `<div class="modal-body text-center"><div class="spinner"></div></div>`;
        modal.classList.remove('hidden');

        try {
            this.prospect = await API.getProspect(id);
            this.render();
        } catch (error) {
            console.error('Failed to load prospect:', error);
            showToast('Failed to load prospect', 'error');
            modal.classList.add('hidden');
        }
    },

    render() {
        const container = document.getElementById('schedule-call-form-container');
        const p = this.prospect;

        // Calculate quick date options
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const in3Days = new Date(today);
        in3Days.setDate(in3Days.getDate() + 3);
        const nextWeek = new Date(today);
        nextWeek.setDate(nextWeek.getDate() + 7);

        const formatDate = (d) => d.toISOString().split('T')[0];
        const formatDisplay = (d) => d.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });

        container.innerHTML = `
            <div class="modal-body">
                <!-- Prospect Info -->
                <div class="card">
                    <div class="card-title">${escapeHtml(p.org_name)}</div>
                    ${p.contact_name ? `<div class="card-subtitle">${escapeHtml(p.contact_name)}</div>` : ''}
                    ${p.tier ? `<span class="tier-badge tier-${p.tier.toLowerCase()}">${p.tier}</span>` : ''}
                </div>

                <!-- Quick Date Buttons -->
                <div class="form-group mt-16">
                    <label class="form-label">Schedule for:</label>
                    <div class="schedule-quick-btns">
                        <button class="btn btn-outline schedule-btn" data-date="${formatDate(today)}">
                            Today
                        </button>
                        <button class="btn btn-outline schedule-btn" data-date="${formatDate(tomorrow)}">
                            Tomorrow
                        </button>
                        <button class="btn btn-outline schedule-btn" data-date="${formatDate(in3Days)}">
                            +3 Days<br><small>${formatDisplay(in3Days)}</small>
                        </button>
                        <button class="btn btn-outline schedule-btn" data-date="${formatDate(nextWeek)}">
                            Next Week<br><small>${formatDisplay(nextWeek)}</small>
                        </button>
                    </div>
                </div>

                <!-- Custom Date -->
                <div class="form-group">
                    <label class="form-label">Or pick a date:</label>
                    <input type="date" class="form-input" id="schedule-custom-date"
                        min="${formatDate(today)}">
                </div>

                <!-- Optional Note -->
                <div class="form-group">
                    <label class="form-label">Note (optional)</label>
                    <input type="text" class="form-input" id="schedule-note"
                        placeholder="e.g., Ask about Q2 initiatives">
                </div>

                <!-- Action Buttons -->
                <div class="modal-actions">
                    <button class="btn btn-secondary" onclick="closeModal('schedule-call-modal')">
                        Cancel
                    </button>
                    <button class="btn btn-primary" id="schedule-custom-btn" disabled>
                        Schedule
                    </button>
                </div>
            </div>
        `;

        // Quick date button handlers
        container.querySelectorAll('.schedule-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                await this.scheduleForDate(btn.dataset.date);
            });
        });

        // Custom date handler
        const customDateInput = document.getElementById('schedule-custom-date');
        const customBtn = document.getElementById('schedule-custom-btn');

        customDateInput.addEventListener('change', () => {
            customBtn.disabled = !customDateInput.value;
        });

        customBtn.addEventListener('click', async () => {
            if (customDateInput.value) {
                await this.scheduleForDate(customDateInput.value);
            }
        });
    },

    async scheduleForDate(date) {
        const note = document.getElementById('schedule-note').value.trim();
        const description = note || `Call ${this.prospect.org_name}`;

        try {
            showLoading();
            await API.scheduleCall(this.prospectId, date, description);
            hideLoading();

            const displayDate = new Date(date + 'T00:00:00').toLocaleDateString('en-US', {
                weekday: 'short',
                month: 'short',
                day: 'numeric'
            });
            showToast(`Scheduled for ${displayDate}`, 'success');

            closeModal('schedule-call-modal');

            // Execute callback if provided (e.g., refresh queue)
            if (this.callback) {
                this.callback();
            }

            // Refresh current view
            if (currentView && currentView.loadData) {
                currentView.loadData();
            } else if (currentView && currentView.render) {
                currentView.render();
            }

        } catch (error) {
            hideLoading();
            console.error('Failed to schedule call:', error);
            showToast('Failed to schedule call', 'error');
        }
    }
};

// Global function to show modal
function showScheduleCallModal(id, callback = null) {
    ScheduleCallView.show(id, callback);
}
