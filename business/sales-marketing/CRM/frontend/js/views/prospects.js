// All Prospects View
// Shows all prospects with status, segment, and state filtering

const ProspectsView = {
    selectedStatuses: ['all'],
    selectedSegments: ['all'],
    selectedOutcomes: ['all'],
    selectedContacted: 'all',
    selectedICP: 'all',
    selectedTier: 'all',
    currentState: 'all',
    currentSort: 'last_contact',
    sortDirection: 'desc',
    viewMode: localStorage.getItem('crm_prospectsViewMode') || 'table',
    prospects: [],
    allStates: [],

    async render() {
        const container = document.getElementById('app');
        container.innerHTML = `
            <div class="view-header">
                <h1>All Prospects</h1>
                <span class="text-muted" id="prospects-count">Loading...</span>
            </div>

            <!-- Compact Filter Row -->
            <div class="filter-row-compact">
                <!-- Status Multi-Select -->
                <div class="dropdown-filter" id="status-dropdown">
                    <button class="dropdown-toggle" id="status-toggle">
                        Status: All <span class="dropdown-arrow">&#9662;</span>
                    </button>
                    <div class="dropdown-menu hidden" id="status-menu">
                        <label class="dropdown-item">
                            <input type="checkbox" value="all" checked> All Statuses
                        </label>
                        <label class="dropdown-item">
                            <input type="checkbox" value="not_contacted"> Not Contacted
                        </label>
                        <label class="dropdown-item">
                            <input type="checkbox" value="contacted"> Contacted
                        </label>
                        <label class="dropdown-item">
                            <input type="checkbox" value="interested"> Interested
                        </label>
                        <label class="dropdown-item">
                            <input type="checkbox" value="converted"> Converted
                        </label>
                        <label class="dropdown-item">
                            <input type="checkbox" value="not_interested"> Not Interested
                        </label>
                    </div>
                </div>

                <!-- Segment Multi-Select -->
                <div class="dropdown-filter" id="segment-dropdown">
                    <button class="dropdown-toggle" id="segment-toggle">
                        Type: All <span class="dropdown-arrow">&#9662;</span>
                    </button>
                    <div class="dropdown-menu hidden" id="segment-menu">
                        <label class="dropdown-item">
                            <input type="checkbox" value="all" checked> All Types
                        </label>
                        <label class="dropdown-item">
                            <input type="checkbox" value="nonprofit"> Nonprofits
                        </label>
                        <label class="dropdown-item">
                            <input type="checkbox" value="foundation"> Foundations
                        </label>
                        <label class="dropdown-item">
                            <input type="checkbox" value="foundation_mgmt"> Fdn Mgmt
                        </label>
                    </div>
                </div>

                <!-- Quick Contact Filter -->
                <select class="form-input form-select filter-select-small" id="contacted-filter">
                    <option value="all">All Contacts</option>
                    <option value="contacted">Called Only</option>
                    <option value="scheduled">Scheduled Only</option>
                    <option value="not_contacted">Never Called</option>
                </select>

                <!-- Call Outcome Multi-Select -->
                <div class="dropdown-filter" id="outcome-dropdown">
                    <button class="dropdown-toggle" id="outcome-toggle">
                        Outcome: All <span class="dropdown-arrow">&#9662;</span>
                    </button>
                    <div class="dropdown-menu hidden" id="outcome-menu">
                        <label class="dropdown-item">
                            <input type="checkbox" value="all" checked> All Outcomes
                        </label>
                        <label class="dropdown-item">
                            <input type="checkbox" value="talked_to_someone"> Talked to Someone
                        </label>
                        <label class="dropdown-item">
                            <input type="checkbox" value="reached_decision_maker"> Reached DM
                        </label>
                        <label class="dropdown-item">
                            <input type="checkbox" value="vm_left"> Left Voicemail
                        </label>
                        <label class="dropdown-item">
                            <input type="checkbox" value="no_answer"> No Answer
                        </label>
                        <label class="dropdown-item">
                            <input type="checkbox" value="sent_email_request"> Email Request
                        </label>
                    </div>
                </div>

                <!-- ICP Score Select -->
                <select class="form-input form-select filter-select-small" id="icp-filter">
                    <option value="all">ICP: All</option>
                    <option value="high">80+ (High)</option>
                    <option value="medium">60-79 (Medium)</option>
                    <option value="low">Below 60 (Low)</option>
                    <option value="not_set">Not Set</option>
                </select>

                <!-- Tier Select -->
                <select class="form-input form-select filter-select-small" id="tier-filter">
                    <option value="all">Tier: All</option>
                    <option value="priority">1-3 (Priority)</option>
                    <option value="other">4-7</option>
                </select>

                <!-- State Select -->
                <select class="form-input form-select filter-select-small" id="state-filter">
                    <option value="all">All States</option>
                </select>

                <!-- Sort Select -->
                <select class="form-input form-select filter-select-small" id="sort-select">
                    <option value="name">Org A-Z</option>
                    <option value="name_desc">Org Z-A</option>
                    <option value="contact">Contact A-Z</option>
                    <option value="segment">Type</option>
                    <option value="state">State</option>
                    <option value="tier">Tier</option>
                    <option value="icp">ICP Score</option>
                    <option value="status">Status</option>
                    <option value="last_contact">Last Contact</option>
                    <option value="call_count"># Calls</option>
                    <option value="newest">Newest</option>
                </select>
            </div>

            <!-- View Toggle -->
            <div class="view-toggle">
                <button class="view-toggle-btn ${this.viewMode === 'table' ? 'active' : ''}" data-mode="table" title="Table View">
                    &#9776;
                </button>
                <button class="view-toggle-btn ${this.viewMode === 'cards' ? 'active' : ''}" data-mode="cards" title="Card View">
                    &#9638;
                </button>
            </div>

            <div id="prospects-list">
                <div class="loading-inline">Loading...</div>
            </div>
        `;

        this.attachFilterHandlers();
        this.attachViewToggle();
        await this.loadProspects();
    },

    attachViewToggle() {
        document.querySelectorAll('.view-toggle-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.viewMode = btn.dataset.mode;
                localStorage.setItem('crm_prospectsViewMode', this.viewMode);
                document.querySelectorAll('.view-toggle-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.applyFiltersAndSort();
            });
        });
    },

    attachFilterHandlers() {
        // Status dropdown toggle
        const statusToggle = document.getElementById('status-toggle');
        const statusMenu = document.getElementById('status-menu');
        const segmentMenu = document.getElementById('segment-menu');
        const outcomeMenu = document.getElementById('outcome-menu');

        statusToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            statusMenu.classList.toggle('hidden');
            segmentMenu.classList.add('hidden');
            outcomeMenu.classList.add('hidden');
        });

        // Segment dropdown toggle
        const segmentToggle = document.getElementById('segment-toggle');
        segmentToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            segmentMenu.classList.toggle('hidden');
            statusMenu.classList.add('hidden');
            outcomeMenu.classList.add('hidden');
        });

        // Outcome dropdown toggle
        const outcomeToggle = document.getElementById('outcome-toggle');
        outcomeToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            outcomeMenu.classList.toggle('hidden');
            statusMenu.classList.add('hidden');
            segmentMenu.classList.add('hidden');
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', () => {
            statusMenu.classList.add('hidden');
            segmentMenu.classList.add('hidden');
            outcomeMenu.classList.add('hidden');
        });

        // Status checkbox handlers
        statusMenu.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', (e) => {
                e.stopPropagation();
                this.handleStatusChange(e.target);
            });
        });

        // Segment checkbox handlers
        segmentMenu.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', (e) => {
                e.stopPropagation();
                this.handleSegmentChange(e.target);
            });
        });

        // Outcome checkbox handlers
        outcomeMenu.querySelectorAll('input[type="checkbox"]').forEach(cb => {
            cb.addEventListener('change', (e) => {
                e.stopPropagation();
                this.handleOutcomeChange(e.target);
            });
        });

        // Contacted filter handler (quick filter for called/not called)
        // This triggers a server-side reload for "Called Only" to ensure all called prospects are fetched
        document.getElementById('contacted-filter').addEventListener('change', (e) => {
            this.selectedContacted = e.target.value;
            // Reload from server when switching to/from "Called Only" for server-side filtering
            this.loadProspects();
        });

        // ICP filter handler
        document.getElementById('icp-filter').addEventListener('change', (e) => {
            this.selectedICP = e.target.value;
            this.applyFiltersAndSort();
        });

        // Tier filter handler
        document.getElementById('tier-filter').addEventListener('change', (e) => {
            this.selectedTier = e.target.value;
            this.applyFiltersAndSort();
        });

        // State filter handler
        document.getElementById('state-filter').addEventListener('change', (e) => {
            this.currentState = e.target.value;
            this.applyFiltersAndSort();
        });

        // Sort handler
        document.getElementById('sort-select').addEventListener('change', (e) => {
            this.currentSort = e.target.value;
            this.applyFiltersAndSort();
        });
    },

    handleStatusChange(checkbox) {
        const statusMenu = document.getElementById('status-menu');
        const allCheckbox = statusMenu.querySelector('input[value="all"]');
        const otherCheckboxes = statusMenu.querySelectorAll('input:not([value="all"])');

        if (checkbox.value === 'all') {
            // If "All" is checked, uncheck others
            if (checkbox.checked) {
                otherCheckboxes.forEach(cb => cb.checked = false);
                this.selectedStatuses = ['all'];
            } else {
                checkbox.checked = true; // Can't uncheck "All" directly
            }
        } else {
            // If a specific status is checked
            if (checkbox.checked) {
                allCheckbox.checked = false;
                this.selectedStatuses = this.selectedStatuses.filter(s => s !== 'all');
                this.selectedStatuses.push(checkbox.value);
            } else {
                this.selectedStatuses = this.selectedStatuses.filter(s => s !== checkbox.value);
                if (this.selectedStatuses.length === 0) {
                    allCheckbox.checked = true;
                    this.selectedStatuses = ['all'];
                }
            }
        }

        this.updateStatusToggleLabel();
        this.applyFiltersAndSort();
    },

    handleSegmentChange(checkbox) {
        const segmentMenu = document.getElementById('segment-menu');
        const allCheckbox = segmentMenu.querySelector('input[value="all"]');
        const otherCheckboxes = segmentMenu.querySelectorAll('input:not([value="all"])');

        if (checkbox.value === 'all') {
            if (checkbox.checked) {
                otherCheckboxes.forEach(cb => cb.checked = false);
                this.selectedSegments = ['all'];
            } else {
                checkbox.checked = true;
            }
        } else {
            if (checkbox.checked) {
                allCheckbox.checked = false;
                this.selectedSegments = this.selectedSegments.filter(s => s !== 'all');
                this.selectedSegments.push(checkbox.value);
            } else {
                this.selectedSegments = this.selectedSegments.filter(s => s !== checkbox.value);
                if (this.selectedSegments.length === 0) {
                    allCheckbox.checked = true;
                    this.selectedSegments = ['all'];
                }
            }
        }

        this.updateSegmentToggleLabel();
        this.applyFiltersAndSort();
    },

    updateStatusToggleLabel() {
        const toggle = document.getElementById('status-toggle');
        if (this.selectedStatuses.includes('all')) {
            toggle.innerHTML = 'Status: All <span class="dropdown-arrow">&#9662;</span>';
        } else if (this.selectedStatuses.length === 1) {
            toggle.innerHTML = `Status: ${formatStatus(this.selectedStatuses[0])} <span class="dropdown-arrow">&#9662;</span>`;
        } else {
            toggle.innerHTML = `Status: ${this.selectedStatuses.length} selected <span class="dropdown-arrow">&#9662;</span>`;
        }
    },

    updateSegmentToggleLabel() {
        const toggle = document.getElementById('segment-toggle');
        if (this.selectedSegments.includes('all')) {
            toggle.innerHTML = 'Type: All <span class="dropdown-arrow">&#9662;</span>';
        } else if (this.selectedSegments.length === 1) {
            toggle.innerHTML = `Type: ${formatSegment(this.selectedSegments[0])} <span class="dropdown-arrow">&#9662;</span>`;
        } else {
            toggle.innerHTML = `Type: ${this.selectedSegments.length} selected <span class="dropdown-arrow">&#9662;</span>`;
        }
    },

    handleOutcomeChange(checkbox) {
        const outcomeMenu = document.getElementById('outcome-menu');
        const allCheckbox = outcomeMenu.querySelector('input[value="all"]');
        const otherCheckboxes = outcomeMenu.querySelectorAll('input:not([value="all"])');

        if (checkbox.value === 'all') {
            if (checkbox.checked) {
                otherCheckboxes.forEach(cb => cb.checked = false);
                this.selectedOutcomes = ['all'];
            } else {
                checkbox.checked = true;
            }
        } else {
            if (checkbox.checked) {
                allCheckbox.checked = false;
                this.selectedOutcomes = this.selectedOutcomes.filter(s => s !== 'all');
                this.selectedOutcomes.push(checkbox.value);
            } else {
                this.selectedOutcomes = this.selectedOutcomes.filter(s => s !== checkbox.value);
                if (this.selectedOutcomes.length === 0) {
                    allCheckbox.checked = true;
                    this.selectedOutcomes = ['all'];
                }
            }
        }

        this.updateOutcomeToggleLabel();
        this.applyFiltersAndSort();
    },

    updateOutcomeToggleLabel() {
        const toggle = document.getElementById('outcome-toggle');
        if (this.selectedOutcomes.includes('all')) {
            toggle.innerHTML = 'Call: All <span class="dropdown-arrow">&#9662;</span>';
        } else if (this.selectedOutcomes.length === 1) {
            toggle.innerHTML = `Call: ${formatOutcomeShort(this.selectedOutcomes[0])} <span class="dropdown-arrow">&#9662;</span>`;
        } else {
            toggle.innerHTML = `Call: ${this.selectedOutcomes.length} selected <span class="dropdown-arrow">&#9662;</span>`;
        }
    },

    async loadProspects() {
        try {
            // Use server-side filtering for special cases
            if (this.selectedContacted === 'contacted') {
                // Called Only - fetch only prospects with calls
                this.prospects = await API.getAllProspectsWithLastCall({
                    limit: 2000,
                    calledOnly: true
                });
            } else if (this.selectedContacted === 'scheduled') {
                // Scheduled Only - fetch only prospects with pending tasks
                this.prospects = await API.getProspectsWithScheduledTasks({ limit: 500 });
            } else {
                // All or Not Contacted - fetch with called prospects prioritized
                this.prospects = await API.getAllProspectsWithLastCall({
                    limit: 2000,
                    calledOnly: false
                });
            }
            this.populateStateFilter();
            this.applyFiltersAndSort();
        } catch (error) {
            console.error('Failed to load prospects:', error);
            showToast('Failed to load prospects', 'error');
        }
    },

    populateStateFilter() {
        // Get unique states from prospects
        const states = [...new Set(this.prospects.map(p => p.state).filter(Boolean))].sort();
        this.allStates = states;

        const stateSelect = document.getElementById('state-filter');
        stateSelect.innerHTML = `<option value="all">All States (${states.length})</option>` +
            states.map(s => `<option value="${s}">${s}</option>`).join('');
    },

    applyFiltersAndSort() {
        let filtered = [...this.prospects];

        // Apply status filter (multi-select)
        if (!this.selectedStatuses.includes('all')) {
            filtered = filtered.filter(p => this.selectedStatuses.includes(p.status));
        }

        // Apply segment filter (multi-select)
        if (!this.selectedSegments.includes('all')) {
            filtered = filtered.filter(p => this.selectedSegments.includes(p.segment));
        }

        // Apply contacted filter (quick filter for called/not called)
        if (this.selectedContacted === 'contacted') {
            filtered = filtered.filter(p => p.call_count > 0);
        } else if (this.selectedContacted === 'not_contacted') {
            filtered = filtered.filter(p => !p.call_count || p.call_count === 0);
        }

        // Apply call outcome filter (multi-select)
        if (!this.selectedOutcomes.includes('all')) {
            filtered = filtered.filter(p => {
                // "Never Called" = no last_call_outcome
                if (this.selectedOutcomes.includes('no_calls') && !p.last_call_outcome) {
                    return true;
                }
                // Match specific outcomes
                return p.last_call_outcome && this.selectedOutcomes.includes(p.last_call_outcome);
            });
        }

        // Apply ICP score filter
        if (this.selectedICP !== 'all') {
            if (this.selectedICP === 'high') {
                filtered = filtered.filter(p => p.icp_score >= 80);
            } else if (this.selectedICP === 'medium') {
                filtered = filtered.filter(p => p.icp_score >= 60 && p.icp_score < 80);
            } else if (this.selectedICP === 'low') {
                filtered = filtered.filter(p => p.icp_score < 60);
            } else if (this.selectedICP === 'not_set') {
                filtered = filtered.filter(p => !p.icp_score);
            }
        }

        // Apply Tier filter
        if (this.selectedTier !== 'all') {
            if (this.selectedTier === 'priority') {
                filtered = filtered.filter(p => p.tier && p.tier <= 3);
            } else if (this.selectedTier === 'other') {
                filtered = filtered.filter(p => p.tier && p.tier > 3);
            }
        }

        // Apply state filter
        if (this.currentState !== 'all') {
            filtered = filtered.filter(p => p.state === this.currentState);
        }

        // Apply sort
        const dir = this.sortDirection === 'asc' ? 1 : -1;
        filtered.sort((a, b) => {
            let result = 0;
            switch (this.currentSort) {
                case 'name':
                    result = (a.org_name || '').localeCompare(b.org_name || '');
                    break;
                case 'name_desc':
                    result = (b.org_name || '').localeCompare(a.org_name || '');
                    break;
                case 'contact':
                    result = (a.contact_name || '').localeCompare(b.contact_name || '');
                    break;
                case 'segment':
                    result = (a.segment || '').localeCompare(b.segment || '');
                    break;
                case 'status':
                    const statusOrder = ['interested', 'contacted', 'not_contacted', 'converted', 'not_interested'];
                    result = statusOrder.indexOf(a.status) - statusOrder.indexOf(b.status);
                    break;
                case 'state':
                    result = (a.state || 'ZZZ').localeCompare(b.state || 'ZZZ');
                    break;
                case 'tier':
                    result = (a.tier || 999) - (b.tier || 999);
                    break;
                case 'icp':
                    result = (b.icp_score || 0) - (a.icp_score || 0);
                    break;
                case 'newest':
                    result = new Date(b.created_at) - new Date(a.created_at);
                    break;
                case 'last_contact':
                    const aDate = a.last_call_date ? new Date(a.last_call_date) : new Date(0);
                    const bDate = b.last_call_date ? new Date(b.last_call_date) : new Date(0);
                    result = bDate - aDate;
                    break;
                case 'call_count':
                    result = (b.call_count || 0) - (a.call_count || 0);
                    break;
                default:
                    result = 0;
            }
            return result * dir;
        });

        this.renderList(filtered);
    },

    renderList(prospects) {
        const listEl = document.getElementById('prospects-list');
        const countEl = document.getElementById('prospects-count');

        countEl.textContent = `${prospects.length} prospects`;

        if (prospects.length === 0) {
            listEl.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">&#128203;</div>
                    <div class="empty-state-title">No Prospects Found</div>
                    <p>No prospects match these filters. Try adjusting your filters or import some data.</p>
                </div>
            `;
            return;
        }

        if (this.viewMode === 'table') {
            this.renderTable(prospects, listEl);
        } else {
            listEl.innerHTML = prospects.map(p => this.renderCard(p)).join('');
            this.attachCardHandlers(listEl);
        }
    },

    renderTable(prospects, container) {
        const sortIcon = (col) => {
            if (this.currentSort !== col) return '';
            return this.sortDirection === 'asc' ? ' &#9650;' : ' &#9660;';
        };

        container.innerHTML = `
            <div class="table-container">
                <table class="prospects-table">
                    <thead>
                        <tr>
                            <th class="sortable" data-sort="name">Organization${sortIcon('name')}</th>
                            <th>Phone</th>
                            <th class="sortable" data-sort="contact">Contact${sortIcon('contact')}</th>
                            <th class="sortable" data-sort="segment">Type${sortIcon('segment')}</th>
                            <th class="sortable" data-sort="state">State${sortIcon('state')}</th>
                            <th class="sortable" data-sort="tier">Tier${sortIcon('tier')}</th>
                            <th class="sortable" data-sort="icp">ICP${sortIcon('icp')}</th>
                            <th class="sortable" data-sort="status">Status${sortIcon('status')}</th>
                            <th class="sortable" data-sort="last_contact">Last Contact${sortIcon('last_contact')}</th>
                            <th class="sortable" data-sort="call_count"># Calls${sortIcon('call_count')}</th>
                            <th>Notes</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${prospects.map(p => this.renderTableRow(p)).join('')}
                    </tbody>
                </table>
            </div>
        `;

        // Attach sort handlers to headers
        container.querySelectorAll('th.sortable').forEach(th => {
            th.addEventListener('click', () => {
                const col = th.dataset.sort;
                if (this.currentSort === col) {
                    this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
                } else {
                    this.currentSort = col;
                    this.sortDirection = 'asc';
                }
                this.applyFiltersAndSort();
            });
        });

        // Enable horizontal scroll with mouse wheel on table
        const tableContainer = container.querySelector('.table-container');
        if (tableContainer) {
            tableContainer.addEventListener('wheel', (e) => {
                // Only convert to horizontal if there's horizontal overflow
                if (tableContainer.scrollWidth > tableContainer.clientWidth) {
                    e.preventDefault();
                    tableContainer.scrollLeft += e.deltaY;
                }
            }, { passive: false });
        }

        // Attach row click handlers
        container.querySelectorAll('tr[data-id]').forEach(row => {
            row.addEventListener('click', (e) => {
                if (e.target.closest('button') || e.target.closest('a')) return;
                showProspectDetail(row.dataset.id);
            });
        });
    },

    renderTableRow(p) {
        const lastContact = p.last_call_date ? formatTimeAgo(p.last_call_date) : '-';
        const orgName = p.org_name || p.contact_name || 'Unknown';
        const notes = p.last_call_notes || p.notes || '';
        const truncatedNotes = notes.length > 40 ? notes.substring(0, 40) + '...' : notes;

        return `
            <tr data-id="${p.id}" class="table-row-clickable">
                <td class="cell-org-name">${escapeHtml(orgName)}</td>
                <td class="cell-phone">${p.phone ? `<a href="tel:${p.phone}" onclick="event.stopPropagation()">${formatPhone(p.phone)}</a>` : '-'}</td>
                <td>${escapeHtml(p.contact_name || '-')}</td>
                <td><span class="badge badge-${p.segment}">${formatSegment(p.segment)}</span></td>
                <td>${p.state || '-'}</td>
                <td>${p.tier || '-'}</td>
                <td>${p.icp_score || '-'}</td>
                <td><span class="badge badge-${p.status}">${formatStatus(p.status)}</span></td>
                <td>${lastContact}</td>
                <td>${p.call_count || 0}</td>
                <td class="cell-notes" title="${escapeHtml(notes)}">${escapeHtml(truncatedNotes) || '-'}</td>
            </tr>
        `;
    },

    attachCardHandlers(container) {
        // Attach card handlers
        container.querySelectorAll('.prospect-card').forEach(card => {
            card.addEventListener('click', (e) => {
                if (e.target.closest('button') || e.target.closest('a')) return;
                showProspectDetail(card.dataset.id);
            });
        });

        // Attach action handlers
        container.querySelectorAll('.btn-log-call').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                showLogCallModal(btn.dataset.id);
            });
        });
    },

    renderCard(prospect) {
        const stateBadge = prospect.state ? `<span class="badge badge-state">${prospect.state}</span>` : '';
        const tierBadge = prospect.tier ? `<span class="badge">Tier ${prospect.tier}</span>` : '';

        // Last contact info
        let lastContactHtml = '';
        if (prospect.last_call_date || prospect.last_call_notes) {
            const contactDate = prospect.last_call_date
                ? formatTimeAgo(prospect.last_call_date)
                : '';
            const contactNote = prospect.last_call_notes
                ? escapeHtml(prospect.last_call_notes.substring(0, 100)) + (prospect.last_call_notes.length > 100 ? '...' : '')
                : '';
            const outcome = prospect.last_call_outcome
                ? `<span class="outcome-badge ${prospect.last_call_outcome}">${formatOutcomeShort(prospect.last_call_outcome)}</span>`
                : '';

            // Interest level badge
            const interestInfo = prospect.last_call_interest ? formatInterest(prospect.last_call_interest) : null;
            const interest = interestInfo
                ? `<span class="interest-badge ${interestInfo.class}" title="${interestInfo.label}">${interestInfo.icon}</span>`
                : '';

            lastContactHtml = `
                <div class="last-contact-info">
                    <div class="last-contact-header">
                        ${outcome}
                        ${interest}
                        <span class="last-contact-date">${contactDate}</span>
                    </div>
                    ${contactNote ? `<div class="last-contact-note">${contactNote}</div>` : ''}
                </div>
            `;
        }

        return `
            <div class="card prospect-card" data-id="${prospect.id}">
                <div class="card-header">
                    <div>
                        <div class="card-title">${escapeHtml(prospect.org_name)}</div>
                        ${prospect.contact_name ? `<div class="card-subtitle">${escapeHtml(prospect.contact_name)}${prospect.contact_title ? ' - ' + escapeHtml(prospect.contact_title) : ''}</div>` : ''}
                    </div>
                    <div class="badge-group">
                        <span class="badge badge-${prospect.status}">${formatStatus(prospect.status)}</span>
                        <span class="badge badge-${prospect.segment}">${formatSegment(prospect.segment)}</span>
                        ${stateBadge}
                        ${tierBadge}
                    </div>
                </div>

                ${prospect.phone ? `
                    <div class="prospect-phone">
                        &#128222; <a href="tel:${prospect.phone}" onclick="event.stopPropagation()">${formatPhone(prospect.phone)}</a>
                    </div>
                ` : ''}

                ${lastContactHtml}

                <div class="prospect-actions">
                    <button class="btn btn-primary btn-small btn-log-call" data-id="${prospect.id}">
                        Log Call
                    </button>
                    <button class="btn btn-secondary btn-small" onclick="event.stopPropagation(); showLogEmailModal(${prospect.id})">
                        Log Email
                    </button>
                </div>
            </div>
        `;
    }
};

// Helper functions
function formatStatus(status) {
    const labels = {
        'not_contacted': 'Not Contacted',
        'contacted': 'Contacted',
        'interested': 'Interested',
        'converted': 'Converted',
        'not_interested': 'Not Interested'
    };
    return labels[status] || status;
}

function formatSegment(segment) {
    const labels = {
        'nonprofit': 'Nonprofit',
        'foundation': 'Foundation',
        'foundation_mgmt': 'Fdn Mgmt'
    };
    return labels[segment] || segment;
}

function formatOutcomeShort(outcome) {
    const labels = {
        'vm_left': 'VM',
        'talked_to_someone': 'Talked',
        'reached_decision_maker': 'DM',
        'no_answer': 'No Ans',
        'wrong_number': 'Wrong #',
        'sent_email_request': 'Email Req',
        'disconnected': 'Disconn',
        'no_calls': 'Never Called'
    };
    return labels[outcome] || outcome;
}

function formatInterest(interest) {
    const icons = {
        'yes': { icon: '✓', class: 'interest-yes', label: 'Interested' },
        'no': { icon: '✗', class: 'interest-no', label: 'Not Interested' },
        'maybe': { icon: '?', class: 'interest-maybe', label: 'Maybe' },
        'uncertain': { icon: '~', class: 'interest-uncertain', label: 'Uncertain' }
    };
    return icons[interest] || null;
}

function formatTimeAgo(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)}mo ago`;
    return `${Math.floor(diffDays / 365)}y ago`;
}
