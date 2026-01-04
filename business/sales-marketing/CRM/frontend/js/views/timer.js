// Timer View - Clock In/Out and Session Tracking
const TimerView = {
    activeSession: null,
    timerInterval: null,
    selectedHours: 2, // Default

    // Initialize timer on app load
    async init() {
        // Check for active session
        await this.checkActiveSession();
        this.renderFloatingTimer();
        this.startTimerUpdate();
    },

    async checkActiveSession() {
        try {
            this.activeSession = await API.getActiveSession();
        } catch (e) {
            console.error('Failed to check active session:', e);
            this.activeSession = null;
        }
    },

    renderFloatingTimer() {
        // Remove existing timer if any
        const existing = document.getElementById('floating-timer');
        if (existing) existing.remove();

        const timer = document.createElement('div');
        timer.id = 'floating-timer';
        timer.className = `floating-timer ${this.activeSession ? '' : 'clocked-out'}`;
        timer.onclick = () => this.handleTimerClick();

        if (this.activeSession) {
            const elapsed = this.formatElapsedTime(this.activeSession.elapsed_seconds || 0);
            const calls = this.activeSession.calls_made || 0;
            timer.innerHTML = `
                <div class="timer-pulse"></div>
                <div class="timer-info">
                    <span class="timer-text">${elapsed}</span>
                    <span class="timer-calls">${calls} call${calls !== 1 ? 's' : ''}</span>
                </div>
            `;
        } else {
            timer.innerHTML = `
                <span class="timer-icon">&#9201;</span>
                <span class="timer-text">Clock In</span>
            `;
        }

        document.body.appendChild(timer);
    },

    formatElapsedTime(seconds) {
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);

        if (hrs > 0) {
            return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    },

    startTimerUpdate() {
        // Update timer every second when clocked in
        if (this.timerInterval) clearInterval(this.timerInterval);

        this.timerInterval = setInterval(() => {
            if (this.activeSession) {
                this.activeSession.elapsed_seconds = (this.activeSession.elapsed_seconds || 0) + 1;
                this.updateTimerDisplay();
            }
        }, 1000);
    },

    updateTimerDisplay() {
        const timerText = document.querySelector('#floating-timer .timer-text');
        if (timerText && this.activeSession) {
            timerText.textContent = this.formatElapsedTime(this.activeSession.elapsed_seconds);
        }
    },

    handleTimerClick() {
        if (this.activeSession) {
            this.showClockOutModal();
        } else {
            this.showClockInModal();
        }
    },

    showClockInModal() {
        const modal = document.getElementById('clock-in-modal');
        if (!modal) return;

        const container = document.getElementById('clock-in-form-container');
        this.selectedHours = 2; // Reset default

        // Calculate suggested calls (5 min avg per call)
        const suggestedCalls = Math.round(this.selectedHours * 60 / 5);

        container.innerHTML = `
            <div class="modal-body">
                <div class="clock-in-summary">
                    <div class="summary-title">Starting a call session</div>
                    <div class="summary-value">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</div>
                </div>

                <div class="form-group">
                    <label class="form-label">How many hours do you have?</label>
                    <div class="hours-selector">
                        <button class="hours-btn" data-hours="0.5">30m</button>
                        <button class="hours-btn" data-hours="1">1h</button>
                        <button class="hours-btn selected" data-hours="2">2h</button>
                        <button class="hours-btn" data-hours="3">3h</button>
                    </div>
                </div>

                <div class="ai-suggestion" id="ai-suggestion">
                    <span class="ai-suggestion-icon">&#129302;</span>
                    <div class="ai-suggestion-text">
                        <div class="ai-suggestion-title">AI Suggests: ${suggestedCalls} calls</div>
                        <div class="ai-suggestion-detail">Based on ~5 min per call average</div>
                    </div>
                </div>

                <div class="modal-actions">
                    <button class="btn btn-secondary" onclick="closeModal('clock-in-modal')">Cancel</button>
                    <button class="btn btn-primary" onclick="TimerView.clockIn()">
                        &#9205; Start Session
                    </button>
                </div>
            </div>
        `;

        // Add hour button listeners
        container.querySelectorAll('.hours-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                container.querySelectorAll('.hours-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                this.selectedHours = parseFloat(btn.dataset.hours);

                // Update AI suggestion
                const suggested = Math.round(this.selectedHours * 60 / 5);
                document.querySelector('#ai-suggestion .ai-suggestion-title').textContent = `AI Suggests: ${suggested} calls`;
            });
        });

        modal.classList.remove('hidden');
    },

    async clockIn() {
        try {
            showLoading();
            const plannedCalls = Math.round(this.selectedHours * 60 / 5);

            const session = await API.clockIn(this.selectedHours, plannedCalls);
            this.activeSession = {
                ...session,
                elapsed_seconds: 0,
                calls_made: 0
            };

            closeModal('clock-in-modal');
            this.renderFloatingTimer();
            showToast(`Clocked in! Target: ${plannedCalls} calls`, 'success');
        } catch (e) {
            showToast('Failed to clock in: ' + e.message, 'error');
        } finally {
            hideLoading();
        }
    },

    showClockOutModal() {
        const modal = document.getElementById('clock-out-modal');
        if (!modal || !this.activeSession) return;

        const container = document.getElementById('clock-out-form-container');
        const elapsed = this.activeSession.elapsed_seconds || 0;
        const hours = (elapsed / 3600).toFixed(1);
        const calls = this.activeSession.calls_made || 0;
        const callsPerHour = elapsed > 0 ? (calls / (elapsed / 3600)).toFixed(1) : 0;
        const plannedCalls = this.activeSession.planned_calls || 0;
        const progress = plannedCalls > 0 ? Math.round((calls / plannedCalls) * 100) : null;

        container.innerHTML = `
            <div class="modal-body">
                <div class="session-summary">
                    <div class="session-summary-row">
                        <span class="session-summary-label">Clock In</span>
                        <span class="session-summary-value">${new Date(this.activeSession.clock_in).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                    </div>
                    <div class="session-summary-row">
                        <span class="session-summary-label">Duration</span>
                        <span class="session-summary-value highlight">${this.formatElapsedTime(elapsed)}</span>
                    </div>
                    <div class="session-summary-row">
                        <span class="session-summary-label">Calls Made</span>
                        <span class="session-summary-value">${calls}${plannedCalls ? ` / ${plannedCalls}` : ''}</span>
                    </div>
                    ${progress !== null ? `
                    <div class="session-summary-row">
                        <span class="session-summary-label">Goal Progress</span>
                        <span class="session-summary-value">${progress}%</span>
                    </div>
                    ` : ''}
                </div>

                <div class="session-performance">
                    <div class="perf-value">${callsPerHour}</div>
                    <div class="perf-label">calls per hour</div>
                </div>

                <div class="form-group mt-24">
                    <label class="form-label">Session Notes (optional)</label>
                    <textarea id="session-notes" class="form-input form-textarea" rows="3"
                        placeholder="What did you accomplish? Any follow-ups needed?"></textarea>
                </div>

                <div class="modal-actions">
                    <button class="btn btn-secondary" onclick="closeModal('clock-out-modal')">Keep Working</button>
                    <button class="btn btn-danger" onclick="TimerView.clockOut()">
                        &#9209; Clock Out
                    </button>
                </div>
            </div>
        `;

        modal.classList.remove('hidden');
    },

    async clockOut() {
        try {
            showLoading();
            const notes = document.getElementById('session-notes')?.value || null;

            await API.clockOut(this.activeSession.id, notes);
            this.activeSession = null;

            closeModal('clock-out-modal');
            this.renderFloatingTimer();
            showToast('Session complete!', 'success');
        } catch (e) {
            showToast('Failed to clock out: ' + e.message, 'error');
        } finally {
            hideLoading();
        }
    },

    // Call this when a call is logged to link it to the session
    async linkCallToSession(callId) {
        if (!this.activeSession) return;

        try {
            await API.updateCallSession(callId, this.activeSession.id);
            this.activeSession.calls_made = (this.activeSession.calls_made || 0) + 1;

            // Update display
            const callsEl = document.querySelector('#floating-timer .timer-calls');
            if (callsEl) {
                const calls = this.activeSession.calls_made;
                callsEl.textContent = `${calls} call${calls !== 1 ? 's' : ''}`;
            }
        } catch (e) {
            console.error('Failed to link call to session:', e);
        }
    },

    // Get current session ID for call logging
    getCurrentSessionId() {
        return this.activeSession?.id || null;
    }
};
