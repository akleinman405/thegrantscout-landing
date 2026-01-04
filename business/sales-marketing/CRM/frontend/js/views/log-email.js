// Log Email Modal
// Email tracking form

const LogEmailView = {
    prospectId: null,
    prospect: null,

    async show(id) {
        this.prospectId = id;
        const modal = document.getElementById('log-email-modal');
        const container = document.getElementById('log-email-form-container');

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
        const container = document.getElementById('log-email-form-container');
        const p = this.prospect;

        container.innerHTML = `
            <div class="modal-body">
                <!-- Prospect Info -->
                <div class="card">
                    <div class="card-title">${escapeHtml(p.org_name)}</div>
                    ${p.contact_name ? `<div class="card-subtitle">${escapeHtml(p.contact_name)}</div>` : ''}
                    ${p.email ? `
                        <a href="mailto:${p.email}" class="btn btn-primary btn-block mt-16">
                            &#128231; Email ${escapeHtml(p.email)}
                        </a>
                    ` : '<p class="text-muted mt-16">No email on file</p>'}
                </div>

                <!-- Direction -->
                <div class="form-group mt-16">
                    <label class="form-label">Direction *</label>
                    <div class="chip-group" id="direction-chips">
                        <button class="chip selected" data-direction="outbound">Sent (Outbound)</button>
                        <button class="chip" data-direction="inbound">Received (Inbound)</button>
                    </div>
                </div>

                <!-- Subject -->
                <div class="form-group">
                    <label class="form-label">Subject</label>
                    <input type="text" class="form-input" id="email-subject"
                        placeholder="Email subject line">
                </div>

                <!-- Body Preview -->
                <div class="form-group">
                    <label class="form-label">Body Preview</label>
                    <textarea class="form-input form-textarea" id="email-body"
                        placeholder="Key content or summary of the email..."
                        rows="4"></textarea>
                </div>

                <!-- Response Date (for outbound) -->
                <div class="form-group" id="response-date-group">
                    <label class="form-label">Response Received On</label>
                    <input type="date" class="form-input" id="email-response-date"
                        max="${new Date().toISOString().split('T')[0]}">
                    <small class="text-muted">If they replied, when?</small>
                </div>

                <!-- Notes -->
                <div class="form-group">
                    <label class="form-label">Notes</label>
                    <textarea class="form-input form-textarea" id="email-notes"
                        placeholder="Additional context..."
                        rows="2"></textarea>
                </div>

                <!-- Submit -->
                <button class="btn btn-success btn-block mt-16" id="save-email-btn">
                    Save Email
                </button>
            </div>
        `;

        // State
        let selectedDirection = 'outbound';

        // Direction chips
        container.querySelectorAll('#direction-chips .chip').forEach(chip => {
            chip.addEventListener('click', () => {
                container.querySelectorAll('#direction-chips .chip').forEach(c => c.classList.remove('selected'));
                chip.classList.add('selected');
                selectedDirection = chip.dataset.direction;

                // Show/hide response date based on direction
                const responseGroup = document.getElementById('response-date-group');
                responseGroup.style.display = selectedDirection === 'outbound' ? 'block' : 'none';
            });
        });

        // Save handler
        document.getElementById('save-email-btn').addEventListener('click', async () => {
            const emailData = {
                prospect_id: this.prospectId,
                direction: selectedDirection,
                subject: document.getElementById('email-subject').value.trim() || null,
                body_preview: document.getElementById('email-body').value.trim() || null,
                response_date: document.getElementById('email-response-date').value || null,
                notes: document.getElementById('email-notes').value.trim() || null
            };

            try {
                showLoading();
                await API.createEmail(emailData);
                hideLoading();
                showToast('Email logged!', 'success');

                // Close modal and refresh
                closeModal('log-email-modal');

                // If prospect modal is open, refresh it
                if (!document.getElementById('prospect-modal').classList.contains('hidden')) {
                    ProspectView.show(this.prospectId);
                }

            } catch (error) {
                hideLoading();
                console.error('Failed to log email:', error);
                showToast('Failed to log email', 'error');
            }
        });
    }
};

// Global function to show modal
function showLogEmailModal(id) {
    LogEmailView.show(id);
}

// Add Task Modal
const AddTaskView = {
    prospectId: null,

    show(prospectId = null) {
        this.prospectId = prospectId;
        const modal = document.getElementById('add-task-modal');
        const container = document.getElementById('add-task-form-container');

        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        const tomorrowStr = tomorrow.toISOString().split('T')[0];

        container.innerHTML = `
            <div class="modal-body">
                ${!prospectId ? `
                    <div class="form-group">
                        <label class="form-label">Search Prospect *</label>
                        <input type="text" class="form-input" id="task-prospect-search"
                            placeholder="Start typing to search...">
                        <div id="task-prospect-results" class="mt-16"></div>
                        <input type="hidden" id="task-prospect-id">
                    </div>
                ` : ''}

                <div class="form-group">
                    <label class="form-label">Task Type</label>
                    <div class="chip-group" id="task-type-chips">
                        <button class="chip selected" data-type="call">Call</button>
                        <button class="chip" data-type="email">Email</button>
                        <button class="chip" data-type="meeting">Meeting</button>
                        <button class="chip" data-type="other">Other</button>
                    </div>
                </div>

                <div class="form-group">
                    <label class="form-label">Due Date *</label>
                    <input type="date" class="form-input" id="task-due-date"
                        value="${tomorrowStr}"
                        min="${new Date().toISOString().split('T')[0]}">
                </div>

                <div class="form-group">
                    <label class="form-label">Description</label>
                    <input type="text" class="form-input" id="task-description"
                        placeholder="What needs to be done?">
                </div>

                <button class="btn btn-success btn-block mt-16" id="save-task-btn">
                    Create Task
                </button>
            </div>
        `;

        modal.classList.remove('hidden');

        // State
        let selectedType = 'call';

        // Type chips
        container.querySelectorAll('#task-type-chips .chip').forEach(chip => {
            chip.addEventListener('click', () => {
                container.querySelectorAll('#task-type-chips .chip').forEach(c => c.classList.remove('selected'));
                chip.classList.add('selected');
                selectedType = chip.dataset.type;
            });
        });

        // Prospect search (if no prospectId provided)
        if (!prospectId) {
            const searchInput = document.getElementById('task-prospect-search');
            let searchTimeout;

            searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                const query = e.target.value;
                if (query.length < 2) {
                    document.getElementById('task-prospect-results').innerHTML = '';
                    return;
                }

                searchTimeout = setTimeout(async () => {
                    const results = await API.searchProspects(query, 5);
                    const resultsContainer = document.getElementById('task-prospect-results');

                    if (results.length === 0) {
                        resultsContainer.innerHTML = '<p class="text-muted">No matches</p>';
                        return;
                    }

                    resultsContainer.innerHTML = results.map(p => `
                        <div class="card" style="cursor: pointer; padding: 8px 12px;"
                             onclick="selectTaskProspect(${p.id}, '${escapeHtml(p.org_name).replace(/'/g, "\\'")}')">
                            <strong>${escapeHtml(p.org_name)}</strong>
                            ${p.contact_name ? '<br><small>' + escapeHtml(p.contact_name) + '</small>' : ''}
                        </div>
                    `).join('');
                }, 300);
            });
        }

        // Save handler
        document.getElementById('save-task-btn').addEventListener('click', async () => {
            const finalProspectId = prospectId || document.getElementById('task-prospect-id').value;

            if (!finalProspectId) {
                showToast('Please select a prospect', 'error');
                return;
            }

            const dueDate = document.getElementById('task-due-date').value;
            if (!dueDate) {
                showToast('Please select a due date', 'error');
                return;
            }

            const taskData = {
                prospect_id: parseInt(finalProspectId),
                type: selectedType,
                due_date: dueDate,
                description: document.getElementById('task-description').value.trim() || null
            };

            try {
                showLoading();
                await API.createTask(taskData);
                hideLoading();
                showToast('Task created!', 'success');
                closeModal('add-task-modal');

                // Refresh tasks view if open
                if (currentView === TasksView) {
                    TasksView.loadTasks();
                }
            } catch (error) {
                hideLoading();
                console.error('Failed to create task:', error);
                showToast('Failed to create task', 'error');
            }
        });
    }
};

// Global helper for prospect selection in task modal
function selectTaskProspect(id, name) {
    document.getElementById('task-prospect-id').value = id;
    document.getElementById('task-prospect-search').value = name;
    document.getElementById('task-prospect-results').innerHTML = `
        <div class="card" style="background: var(--gray-50); padding: 8px 12px;">
            Selected: <strong>${name}</strong>
        </div>
    `;
}

function showAddTaskModal(prospectId = null) {
    AddTaskView.show(prospectId);
}
