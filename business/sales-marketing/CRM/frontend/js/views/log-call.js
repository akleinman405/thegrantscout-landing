// Log Call Modal
// Quick call logging form optimized for mobile

const LogCallView = {
    prospectId: null,
    prospect: null,
    taskId: null, // Optional: task to complete when call is logged

    async show(id, taskId = null) {
        this.prospectId = id;
        this.taskId = taskId;
        const modal = document.getElementById('log-call-modal');
        const container = document.getElementById('log-call-form-container');

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
        const container = document.getElementById('log-call-form-container');
        const p = this.prospect;

        container.innerHTML = `
            <div class="modal-body">
                <!-- Prospect Info -->
                <div class="card">
                    <div class="card-title">${escapeHtml(p.org_name)}</div>
                    ${p.contact_name ? `<div class="card-subtitle">${escapeHtml(p.contact_name)}</div>` : ''}
                    ${p.phone ? `
                        <a href="tel:${p.phone}" class="btn btn-primary btn-block mt-16">
                            &#128222; Call ${formatPhone(p.phone)}
                        </a>
                    ` : ''}
                </div>

                <!-- Outcome -->
                <div class="form-group mt-16">
                    <label class="form-label">Outcome *</label>
                    <div class="chip-group" id="outcome-chips">
                        <button class="chip" data-outcome="vm_left">VM Left</button>
                        <button class="chip" data-outcome="talked_to_someone">Talked</button>
                        <button class="chip" data-outcome="reached_decision_maker">Reached DM</button>
                        <button class="chip" data-outcome="no_answer">No Answer</button>
                        <button class="chip" data-outcome="wrong_number">Wrong #</button>
                        <button class="chip" data-outcome="sent_email_request">Email Request</button>
                        <button class="chip" data-outcome="disconnected">Disconnected</button>
                    </div>
                </div>

                <!-- Interest Level -->
                <div class="form-group">
                    <label class="form-label">Interest Level</label>
                    <div class="chip-group" id="interest-chips">
                        <button class="chip" data-interest="yes" style="--chip-color: var(--success)">Yes</button>
                        <button class="chip" data-interest="maybe">Maybe</button>
                        <button class="chip" data-interest="no" style="--chip-color: var(--danger)">No</button>
                        <button class="chip" data-interest="uncertain">Uncertain</button>
                    </div>
                </div>

                <!-- Duration -->
                <div class="form-group">
                    <label class="form-label">Duration (minutes)</label>
                    <input type="number" class="form-input" id="call-duration"
                        placeholder="Optional" min="1" max="180" inputmode="numeric">
                </div>

                <!-- Notes -->
                <div class="form-group">
                    <label class="form-label">Notes</label>
                    <textarea class="form-input form-textarea" id="call-notes"
                        placeholder="What happened? Key takeaways..."
                        rows="4"></textarea>
                </div>

                <!-- Follow-up -->
                <div class="form-group">
                    <label class="form-label">Follow-up Date</label>
                    <input type="date" class="form-input" id="call-followup"
                        min="${new Date().toISOString().split('T')[0]}">
                </div>

                <!-- Create Task checkbox -->
                <div class="form-group">
                    <label style="display: flex; align-items: center; gap: 8px;">
                        <input type="checkbox" id="create-task" checked>
                        Create follow-up task
                    </label>
                </div>

                <!-- Submit -->
                <button class="btn btn-success btn-block mt-16" id="save-call-btn">
                    Save & Continue
                </button>
            </div>
        `;

        // State
        let selectedOutcome = null;
        let selectedInterest = null;

        // Outcome chips
        container.querySelectorAll('#outcome-chips .chip').forEach(chip => {
            chip.addEventListener('click', () => {
                container.querySelectorAll('#outcome-chips .chip').forEach(c => c.classList.remove('selected'));
                chip.classList.add('selected');
                selectedOutcome = chip.dataset.outcome;
            });
        });

        // Interest chips
        container.querySelectorAll('#interest-chips .chip').forEach(chip => {
            chip.addEventListener('click', () => {
                container.querySelectorAll('#interest-chips .chip').forEach(c => c.classList.remove('selected'));
                chip.classList.add('selected');
                selectedInterest = chip.dataset.interest;
            });
        });

        // Save handler
        document.getElementById('save-call-btn').addEventListener('click', async () => {
            if (!selectedOutcome) {
                showToast('Please select an outcome', 'error');
                return;
            }

            const callData = {
                prospect_id: this.prospectId,
                outcome: selectedOutcome,
                interest: selectedInterest,
                duration_minutes: document.getElementById('call-duration').value || null,
                notes: document.getElementById('call-notes').value.trim() || null,
                follow_up_date: document.getElementById('call-followup').value || null,
                work_session_id: TimerView.getCurrentSessionId() // Link to active session
            };

            const createTask = document.getElementById('create-task').checked;
            const followUpDate = document.getElementById('call-followup').value;

            try {
                showLoading();

                // Create call record
                const createdCall = await API.createCall(callData);

                // Update timer call count if clocked in
                if (createdCall && createdCall[0] && TimerView.activeSession) {
                    TimerView.activeSession.calls_made = (TimerView.activeSession.calls_made || 0) + 1;
                    const callsEl = document.querySelector('#floating-timer .timer-calls');
                    if (callsEl) {
                        const calls = TimerView.activeSession.calls_made;
                        callsEl.textContent = `${calls} call${calls !== 1 ? 's' : ''}`;
                    }
                }

                // Complete the scheduled task if this was from the queue
                if (this.taskId) {
                    await API.completeTask(this.taskId);
                }

                // Auto-update status to 'contacted' if not already progressed further
                if (this.prospect.status === 'not_contacted') {
                    await API.updateProspect(this.prospectId, {
                        status: 'contacted',
                        last_contacted_at: new Date().toISOString()
                    });
                } else {
                    // Just update last_contacted_at
                    await API.updateProspect(this.prospectId, {
                        last_contacted_at: new Date().toISOString()
                    });
                }

                // Create task if requested
                if (createTask && followUpDate) {
                    await API.createTask({
                        prospect_id: this.prospectId,
                        due_date: followUpDate,
                        type: 'call',
                        description: `Follow up with ${p.org_name}`
                    });
                }

                hideLoading();
                showToast('Call logged!', 'success');

                // Close modal and refresh
                closeModal('log-call-modal');

                // If prospect modal is open, refresh it
                if (!document.getElementById('prospect-modal').classList.contains('hidden')) {
                    ProspectView.show(this.prospectId);
                }

                // Refresh current view if it has a loadQueue or similar
                if (currentView && currentView.loadQueue) {
                    currentView.loadQueue();
                } else if (currentView && currentView.render) {
                    currentView.render();
                }

            } catch (error) {
                hideLoading();
                console.error('Failed to log call:', error);
                showToast('Failed to log call', 'error');
            }
        });
    }
};

// Global function to show modal
function showLogCallModal(id, taskId = null) {
    LogCallView.show(id, taskId);
}
