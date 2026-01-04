// Prospect Detail View
// Full prospect info with call/email history

const ProspectView = {
    prospect: null,
    calls: [],
    emails: [],
    tasks: [],
    conversations: [],
    editingCallId: null,
    queueList: null,      // List of prospects in current view
    currentIndex: null,   // Current position in the list

    async show(id, queueList = null, currentIndex = null) {
        this.queueList = queueList;
        this.currentIndex = currentIndex;
        const modal = document.getElementById('prospect-modal');
        const container = document.getElementById('prospect-detail-container');

        container.innerHTML = `
            <div class="modal-body">
                <div class="text-center"><div class="spinner"></div></div>
            </div>
        `;
        modal.classList.remove('hidden');

        // Set up navigation buttons
        this.setupNavButtons();

        try {
            const data = await API.getProspectWithHistory(id);
            this.prospect = data.prospect;
            this.calls = data.calls;
            this.emails = data.emails;
            this.tasks = data.tasks;
            this.editingCallId = null;

            // Also fetch email conversations (from Gmail sync)
            try {
                this.conversations = await API.getProspectConversations(id);
            } catch (e) {
                this.conversations = [];
            }

            this.render();
        } catch (error) {
            console.error('Failed to load prospect:', error);
            showToast('Failed to load prospect', 'error');
            modal.classList.add('hidden');
        }
    },

    setupNavButtons() {
        const prevBtn = document.getElementById('prev-prospect-btn');
        const nextBtn = document.getElementById('next-prospect-btn');

        // Enable/disable based on queue context
        if (this.queueList && this.currentIndex !== null) {
            prevBtn.disabled = this.currentIndex <= 0;
            nextBtn.disabled = this.currentIndex >= this.queueList.length - 1;

            prevBtn.onclick = () => this.navigatePrev();
            nextBtn.onclick = () => this.navigateNext();
        } else {
            prevBtn.disabled = true;
            nextBtn.disabled = true;
        }
    },

    navigatePrev() {
        if (!this.queueList || this.currentIndex <= 0) return;
        this.currentIndex--;
        const prevProspect = this.queueList[this.currentIndex];
        this.show(prevProspect.id || prevProspect.prospect_id, this.queueList, this.currentIndex);
    },

    navigateNext() {
        if (!this.queueList || this.currentIndex >= this.queueList.length - 1) return;
        this.currentIndex++;
        const nextProspect = this.queueList[this.currentIndex];
        this.show(nextProspect.id || nextProspect.prospect_id, this.queueList, this.currentIndex);
    },

    render() {
        const p = this.prospect;
        const container = document.getElementById('prospect-detail-container');

        container.innerHTML = `
            <div class="modal-body">
                <!-- Header -->
                <div class="card">
                    <div class="card-header">
                        <div>
                            <div class="card-title" style="font-size: 1.25rem;">${escapeHtml(p.org_name)}</div>
                            ${p.contact_name ? `<div class="card-subtitle">${escapeHtml(p.contact_name)}${p.contact_title ? ' - ' + escapeHtml(p.contact_title) : ''}</div>` : ''}
                        </div>
                        <div style="display: flex; gap: 8px; align-items: center;">
                            <span class="badge badge-${p.status}">${formatStatus(p.status)}</span>
                            <button class="btn btn-small btn-secondary" id="edit-prospect-btn" title="Edit Prospect">
                                &#9998;
                            </button>
                        </div>
                    </div>

                    <div style="display: grid; gap: 8px; margin-top: 12px;">
                        ${p.phone ? `
                            <a href="tel:${p.phone}" class="btn btn-primary btn-block">
                                &#128222; Call ${formatPhone(p.phone)}
                            </a>
                        ` : ''}
                        ${p.email ? `
                            <a href="mailto:${p.email}" class="btn btn-secondary btn-block">
                                &#128231; ${escapeHtml(p.email)}
                            </a>
                        ` : ''}
                        ${p.website ? `
                            <a href="${p.website.startsWith('http') ? p.website : 'https://' + p.website}"
                               target="_blank" class="btn btn-secondary btn-block">
                                &#127760; Website
                            </a>
                        ` : ''}
                        ${p.linkedin_url ? `
                            <a href="${p.linkedin_url}" target="_blank" class="btn btn-secondary btn-block">
                                LinkedIn
                            </a>
                        ` : ''}
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="flex gap-8 mt-16">
                    <button class="btn btn-primary flex-1" onclick="showLogCallModal(${p.id})">
                        Log Call
                    </button>
                    <button class="btn btn-secondary flex-1" onclick="showLogEmailModal(${p.id})">
                        Log Email
                    </button>
                </div>

                <!-- Description/Mission -->
                ${p.description ? `
                <div class="card mt-16">
                    <h3>About</h3>
                    <p style="font-size: 0.9rem; line-height: 1.5; margin-top: 8px;">${escapeHtml(p.description)}</p>
                </div>
                ` : ''}

                <!-- Details -->
                <div class="card mt-16">
                    <h3>Details</h3>
                    <table style="width: 100%; font-size: 0.875rem; margin-top: 12px;">
                        <tr><td class="text-muted" style="width: 40%;">Segment</td><td>${formatSegment(p.segment)}</td></tr>
                        ${p.ein ? `<tr><td class="text-muted">EIN</td><td>${escapeHtml(p.ein)}</td></tr>` : ''}
                        ${p.city || p.state ? `<tr><td class="text-muted">Location</td><td>${[p.city, p.state].filter(Boolean).join(', ')}</td></tr>` : ''}
                        ${p.timezone ? `<tr><td class="text-muted">Timezone</td><td>${escapeHtml(p.timezone)} Time</td></tr>` : ''}
                        ${p.tier ? `<tr><td class="text-muted">Tier</td><td>Tier ${p.tier}</td></tr>` : ''}
                        ${p.icp_score ? `<tr><td class="text-muted">ICP Score</td><td>${p.icp_score}</td></tr>` : ''}
                        ${p.ntee_code ? `<tr><td class="text-muted">NTEE</td><td>${escapeHtml(p.ntee_code)}</td></tr>` : ''}
                        ${p.annual_budget ? `<tr><td class="text-muted">Budget</td><td>$${Number(p.annual_budget).toLocaleString()}</td></tr>` : ''}
                        ${p.last_contacted_at ? `<tr><td class="text-muted">Last Contacted</td><td>${formatTimeAgo(p.last_contacted_at)}</td></tr>` : ''}
                        ${p.call_count ? `<tr><td class="text-muted">Calls Made</td><td>${p.call_count}</td></tr>` : ''}
                    </table>

                    ${p.notes ? `
                        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--gray-200);">
                            <strong>Notes:</strong>
                            <p style="margin-top: 4px;">${escapeHtml(p.notes)}</p>
                        </div>
                    ` : ''}
                </div>

                <!-- Status Update -->
                <div class="card mt-16">
                    <h3>Update Status</h3>
                    <div class="chip-group mt-16" id="status-chips">
                        ${['not_contacted', 'contacted', 'interested', 'not_interested', 'converted'].map(s => `
                            <button class="chip ${p.status === s ? 'selected' : ''}" data-status="${s}">
                                ${formatStatus(s)}
                            </button>
                        `).join('')}
                    </div>
                </div>

                <!-- Pending Tasks -->
                ${this.tasks.filter(t => !t.completed).length > 0 ? `
                    <div class="card mt-16">
                        <h3>Pending Tasks</h3>
                        ${this.tasks.filter(t => !t.completed).map(t => `
                            <div class="activity-item">
                                <div class="activity-content">
                                    <div class="activity-title">${escapeHtml(t.description || 'Follow up')}</div>
                                    <div class="activity-meta">Due: ${formatDate(t.due_date)} &middot; ${t.type}</div>
                                </div>
                                <button class="btn btn-success btn-small" onclick="completeTaskFromProspect(${t.id})">Done</button>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}

                <!-- Call History -->
                <div class="card mt-16">
                    <h3>Call History (${this.calls.length})</h3>
                    ${this.calls.length === 0 ? '<p class="text-muted">No calls logged yet</p>' : ''}
                    ${this.calls.map(c => this.renderCallItem(c)).join('')}
                </div>

                <!-- Email History (Logged) -->
                <div class="card mt-16">
                    <h3>Logged Emails (${this.emails.length})</h3>
                    ${this.emails.length === 0 ? '<p class="text-muted">No emails logged yet</p>' : ''}
                    ${this.emails.map(e => `
                        <div class="activity-item">
                            <div class="activity-icon">${e.direction === 'inbound' ? '&#128229;' : '&#128228;'}</div>
                            <div class="activity-content">
                                <div class="activity-title">${escapeHtml(e.subject || 'No subject')}</div>
                                <div class="activity-meta">
                                    ${e.direction === 'inbound' ? 'Received' : 'Sent'} &middot;
                                    ${formatTimeAgo(e.sent_date)}
                                </div>
                                ${e.body_preview ? `<p style="margin-top: 4px; font-size: 0.875rem;">${escapeHtml(e.body_preview.substring(0, 150))}${e.body_preview.length > 150 ? '...' : ''}</p>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>

                <!-- Email Conversations (Gmail Sync) -->
                <div class="card mt-16">
                    <h3>&#128231; Email Thread (${this.conversations.length})</h3>
                    ${this.conversations.length === 0 ? '<p class="text-muted">No email conversations synced yet. Run sync_email_conversations.py to populate.</p>' : ''}
                    ${this.conversations.map(c => `
                        <div class="activity-item" style="border-left: 3px solid ${c.direction === 'inbound' ? 'var(--success)' : 'var(--primary)'}; padding-left: 12px;">
                            <div class="activity-icon">${c.direction === 'inbound' ? '&#128229;' : '&#128228;'}</div>
                            <div class="activity-content" style="flex: 1;">
                                <div class="activity-title">
                                    ${escapeHtml(c.subject || 'No subject')}
                                    ${c.is_reply ? '<span style="background: var(--success); color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; margin-left: 8px;">REPLY</span>' : ''}
                                </div>
                                <div class="activity-meta">
                                    ${c.direction === 'inbound' ? '← Received from' : '→ Sent to'} ${escapeHtml(c.email_address || '')}
                                    &middot; ${formatTimeAgo(c.sent_at)}
                                </div>
                                ${c.body_preview ? `<p style="margin-top: 8px; font-size: 0.875rem; background: var(--gray-100); padding: 8px; border-radius: 4px; white-space: pre-wrap;">${escapeHtml(c.body_preview.substring(0, 300))}${c.body_preview.length > 300 ? '...' : ''}</p>` : ''}
                                ${c.direction === 'inbound' ? `
                                    <div style="margin-top: 8px; display: flex; gap: 8px; align-items: center;">
                                        <select class="form-select" id="sentiment-${c.id}" style="flex: 0 0 auto; width: 160px; font-size: 0.875rem;">
                                            <option value="unclassified" ${(!c.reply_sentiment || c.reply_sentiment === 'unclassified') ? 'selected' : ''}>Unclassified</option>
                                            <option value="interested" ${c.reply_sentiment === 'interested' ? 'selected' : ''}>Interested</option>
                                            <option value="not_interested" ${c.reply_sentiment === 'not_interested' ? 'selected' : ''}>Not Interested</option>
                                            <option value="question" ${c.reply_sentiment === 'question' ? 'selected' : ''}>Question</option>
                                            <option value="meeting" ${c.reply_sentiment === 'meeting' ? 'selected' : ''}>Meeting</option>
                                            <option value="forwarded" ${c.reply_sentiment === 'forwarded' ? 'selected' : ''}>Forwarded</option>
                                            <option value="out_of_office" ${c.reply_sentiment === 'out_of_office' ? 'selected' : ''}>Out of Office</option>
                                        </select>
                                        <button class="btn btn-small btn-primary" onclick="ProspectView.saveSentiment(${c.id})">
                                            Save
                                        </button>
                                        ${c.reply_sentiment && c.reply_sentiment !== 'unclassified' ? '<span style="color: var(--success); font-size: 1.2rem;">&#10004;</span>' : ''}
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>

                <!-- Danger Zone -->
                <div class="card mt-16" style="border: 1px solid var(--danger);">
                    <h3 style="color: var(--danger);">Danger Zone</h3>
                    <button class="btn btn-danger btn-block mt-16" id="delete-prospect-btn">
                        Delete Prospect
                    </button>
                </div>
            </div>
        `;

        // Attach handlers
        container.querySelectorAll('#status-chips .chip').forEach(chip => {
            chip.addEventListener('click', () => this.updateStatus(chip.dataset.status));
        });

        document.getElementById('delete-prospect-btn').addEventListener('click', () => this.deleteProspect());
        document.getElementById('edit-prospect-btn').addEventListener('click', () => this.showEditProspectForm());

        // Attach call edit handlers
        container.querySelectorAll('.btn-edit-call').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.startEditCall(parseInt(btn.dataset.callId));
            });
        });

        container.querySelectorAll('.btn-save-call').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.saveCallEdit(parseInt(btn.dataset.callId));
            });
        });

        container.querySelectorAll('.btn-cancel-call-edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.cancelCallEdit();
            });
        });
    },

    renderCallItem(c) {
        const isEditing = this.editingCallId === c.id;

        if (isEditing) {
            return `
                <div class="activity-item" style="flex-direction: column; align-items: stretch;">
                    <div style="display: flex; gap: 8px; margin-bottom: 8px;">
                        <div class="activity-icon">&#128222;</div>
                        <div style="flex: 1;">
                            <div class="activity-title">${formatOutcome(c.outcome)}</div>
                            <div class="activity-meta">${formatTimeAgo(c.call_date)}</div>
                        </div>
                    </div>
                    <div class="form-group" style="margin-bottom: 8px;">
                        <label class="form-label">Interest Level</label>
                        <select class="form-input form-select" id="edit-call-interest-${c.id}">
                            <option value="">None</option>
                            <option value="yes" ${c.interest === 'yes' ? 'selected' : ''}>Yes</option>
                            <option value="maybe" ${c.interest === 'maybe' ? 'selected' : ''}>Maybe</option>
                            <option value="no" ${c.interest === 'no' ? 'selected' : ''}>No</option>
                            <option value="uncertain" ${c.interest === 'uncertain' ? 'selected' : ''}>Uncertain</option>
                        </select>
                    </div>
                    <div class="form-group" style="margin-bottom: 8px;">
                        <label class="form-label">Notes</label>
                        <textarea class="form-input form-textarea" id="edit-call-notes-${c.id}" rows="3">${escapeHtml(c.notes || '')}</textarea>
                    </div>
                    <div class="form-group" style="margin-bottom: 8px;">
                        <label class="form-label">Follow-up Date</label>
                        <input type="date" class="form-input" id="edit-call-followup-${c.id}" value="${c.follow_up_date || ''}">
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button class="btn btn-primary btn-small btn-save-call" data-call-id="${c.id}">Save</button>
                        <button class="btn btn-secondary btn-small btn-cancel-call-edit" data-call-id="${c.id}">Cancel</button>
                    </div>
                </div>
            `;
        }

        return `
            <div class="activity-item">
                <div class="activity-icon">&#128222;</div>
                <div class="activity-content" style="flex: 1;">
                    <div class="activity-title">${formatOutcome(c.outcome)}</div>
                    <div class="activity-meta">
                        ${c.interest ? 'Interest: ' + c.interest + ' &middot; ' : ''}
                        ${formatTimeAgo(c.call_date)}
                        ${c.duration_minutes ? ' &middot; ' + c.duration_minutes + ' min' : ''}
                    </div>
                    ${c.notes ? `<p style="margin-top: 4px; font-size: 0.875rem;">${escapeHtml(c.notes)}</p>` : ''}
                    ${c.follow_up_date ? `<div class="text-muted" style="font-size: 0.75rem;">Follow-up: ${formatDate(c.follow_up_date)}</div>` : ''}
                </div>
                <button class="btn btn-small btn-secondary btn-edit-call" data-call-id="${c.id}" title="Edit">
                    &#9998;
                </button>
            </div>
        `;
    },

    startEditCall(callId) {
        this.editingCallId = callId;
        this.render();
    },

    cancelCallEdit() {
        this.editingCallId = null;
        this.render();
    },

    async saveCallEdit(callId) {
        const interest = document.getElementById(`edit-call-interest-${callId}`).value || null;
        const notes = document.getElementById(`edit-call-notes-${callId}`).value.trim() || null;
        const followUp = document.getElementById(`edit-call-followup-${callId}`).value || null;

        try {
            await API.updateCall(callId, {
                interest: interest,
                notes: notes,
                follow_up_date: followUp
            });

            // Update local data
            const call = this.calls.find(c => c.id === callId);
            if (call) {
                call.interest = interest;
                call.notes = notes;
                call.follow_up_date = followUp;
            }

            this.editingCallId = null;
            showToast('Call updated', 'success');
            this.render();
        } catch (error) {
            console.error('Failed to update call:', error);
            showToast('Failed to update call', 'error');
        }
    },

    showEditProspectForm() {
        const p = this.prospect;
        const container = document.getElementById('prospect-detail-container');

        container.innerHTML = `
            <div class="modal-body">
                <h2 style="margin-bottom: 16px;">Edit Prospect</h2>

                <div class="form-group">
                    <label class="form-label">Organization Name *</label>
                    <input type="text" class="form-input" id="edit-org-name" value="${escapeHtml(p.org_name)}" required>
                </div>

                <div class="form-group">
                    <label class="form-label">Contact Name</label>
                    <input type="text" class="form-input" id="edit-contact-name" value="${escapeHtml(p.contact_name || '')}">
                </div>

                <div class="form-group">
                    <label class="form-label">Contact Title</label>
                    <input type="text" class="form-input" id="edit-contact-title" value="${escapeHtml(p.contact_title || '')}">
                </div>

                <div class="form-group">
                    <label class="form-label">Phone</label>
                    <input type="tel" class="form-input" id="edit-phone" value="${escapeHtml(p.phone || '')}">
                </div>

                <div class="form-group">
                    <label class="form-label">Email</label>
                    <input type="email" class="form-input" id="edit-email" value="${escapeHtml(p.email || '')}">
                </div>

                <div class="form-group">
                    <label class="form-label">Website</label>
                    <input type="url" class="form-input" id="edit-website" value="${escapeHtml(p.website || '')}" placeholder="https://...">
                </div>

                <div class="form-group">
                    <label class="form-label">LinkedIn URL</label>
                    <input type="url" class="form-input" id="edit-linkedin" value="${escapeHtml(p.linkedin_url || '')}" placeholder="https://linkedin.com/...">
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                    <div class="form-group">
                        <label class="form-label">City</label>
                        <input type="text" class="form-input" id="edit-city" value="${escapeHtml(p.city || '')}">
                    </div>
                    <div class="form-group">
                        <label class="form-label">State</label>
                        <input type="text" class="form-input" id="edit-state" value="${escapeHtml(p.state || '')}" maxlength="2" placeholder="CA">
                    </div>
                </div>

                <div class="form-group">
                    <label class="form-label">Notes</label>
                    <textarea class="form-input form-textarea" id="edit-notes" rows="4">${escapeHtml(p.notes || '')}</textarea>
                </div>

                <div style="display: flex; gap: 12px; margin-top: 20px;">
                    <button class="btn btn-primary flex-1" id="save-prospect-btn">Save Changes</button>
                    <button class="btn btn-secondary flex-1" id="cancel-edit-btn">Cancel</button>
                </div>
            </div>
        `;

        document.getElementById('save-prospect-btn').addEventListener('click', () => this.saveProspectEdit());
        document.getElementById('cancel-edit-btn').addEventListener('click', () => this.render());
    },

    async saveProspectEdit() {
        const orgName = document.getElementById('edit-org-name').value.trim();
        if (!orgName) {
            showToast('Organization name is required', 'error');
            return;
        }

        const updates = {
            org_name: orgName,
            contact_name: document.getElementById('edit-contact-name').value.trim() || null,
            contact_title: document.getElementById('edit-contact-title').value.trim() || null,
            phone: document.getElementById('edit-phone').value.trim() || null,
            email: document.getElementById('edit-email').value.trim() || null,
            website: document.getElementById('edit-website').value.trim() || null,
            linkedin_url: document.getElementById('edit-linkedin').value.trim() || null,
            city: document.getElementById('edit-city').value.trim() || null,
            state: document.getElementById('edit-state').value.trim().toUpperCase() || null,
            notes: document.getElementById('edit-notes').value.trim() || null
        };

        try {
            showLoading();
            await API.updateProspect(this.prospect.id, updates);

            // Update local data
            Object.assign(this.prospect, updates);

            hideLoading();
            showToast('Prospect updated', 'success');
            this.render();

            // Refresh current view if needed
            if (currentView && currentView.render) {
                currentView.render();
            }
        } catch (error) {
            hideLoading();
            console.error('Failed to update prospect:', error);
            showToast('Failed to update prospect', 'error');
        }
    },

    async updateStatus(newStatus) {
        try {
            await API.updateProspect(this.prospect.id, { status: newStatus });
            this.prospect.status = newStatus;

            // Update UI
            document.querySelectorAll('#status-chips .chip').forEach(chip => {
                chip.classList.toggle('selected', chip.dataset.status === newStatus);
            });

            showToast('Status updated', 'success');
        } catch (error) {
            console.error('Failed to update status:', error);
            showToast('Failed to update status', 'error');
        }
    },

    async deleteProspect() {
        if (!confirm(`Delete "${this.prospect.org_name}"? This cannot be undone.`)) return;

        try {
            await API.deleteProspect(this.prospect.id);
            showToast('Prospect deleted', 'success');
            closeModal('prospect-modal');
            // Refresh current view
            if (currentView && currentView.render) {
                currentView.render();
            }
        } catch (error) {
            console.error('Failed to delete prospect:', error);
            showToast('Failed to delete prospect', 'error');
        }
    },

    async saveSentiment(conversationId) {
        const selectElement = document.getElementById(`sentiment-${conversationId}`);
        const sentiment = selectElement.value;

        try {
            await API.updateConversationSentiment(conversationId, sentiment);

            // Update local data
            const conversation = this.conversations.find(c => c.id === conversationId);
            if (conversation) {
                conversation.reply_sentiment = sentiment;
            }

            showToast('Sentiment saved', 'success');
            this.render();
        } catch (error) {
            console.error('Failed to save sentiment:', error);
            showToast('Failed to save sentiment', 'error');
        }
    }
};

// Global helper for task completion from prospect view
async function completeTaskFromProspect(taskId) {
    try {
        await API.completeTask(taskId);
        showToast('Task completed!', 'success');
        // Refresh prospect view
        ProspectView.show(ProspectView.prospect.id);
    } catch (error) {
        console.error('Failed to complete task:', error);
        showToast('Failed to complete task', 'error');
    }
}
