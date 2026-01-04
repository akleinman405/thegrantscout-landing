// Import View
// CSV upload and prospect import

const ImportView = {
    csvData: null,
    columnMapping: {},
    sourceName: '',
    sourceCriteria: '',
    defaultSegment: 'nonprofit',

    async render() {
        const container = document.getElementById('app');
        container.innerHTML = `
            <div class="view-header">
                <h1>Import Prospects</h1>
            </div>

            <div id="import-step-1">
                <div class="drop-zone" id="drop-zone">
                    <input type="file" class="file-input" id="file-input" accept=".csv">
                    <div class="drop-zone-text">
                        <p><strong>Drop CSV file here</strong></p>
                        <p>or click to browse</p>
                    </div>
                </div>
            </div>

            <div id="import-step-2" class="hidden">
                <!-- Column mapping UI -->
            </div>

            <div id="import-step-3" class="hidden">
                <!-- Preview and confirm -->
            </div>
        `;

        this.attachDropZoneHandlers();
    },

    attachDropZoneHandlers() {
        const dropZone = document.getElementById('drop-zone');
        const fileInput = document.getElementById('file-input');

        dropZone.addEventListener('click', () => fileInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && file.name.endsWith('.csv')) {
                this.handleFile(file);
            } else {
                showToast('Please upload a CSV file', 'error');
            }
        });

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) this.handleFile(file);
        });
    },

    async handleFile(file) {
        try {
            const text = await file.text();
            this.csvData = this.parseCSV(text);
            this.showMappingStep(file.name);
        } catch (error) {
            console.error('Failed to parse CSV:', error);
            showToast('Failed to parse CSV file', 'error');
        }
    },

    parseCSV(text) {
        const lines = text.split(/\r?\n/).filter(line => line.trim());
        if (lines.length < 2) throw new Error('CSV must have header and at least one row');

        const headers = this.parseCSVLine(lines[0]);
        const rows = lines.slice(1).map(line => {
            const values = this.parseCSVLine(line);
            const row = {};
            headers.forEach((h, i) => row[h] = values[i] || '');
            return row;
        });

        return { headers, rows };
    },

    parseCSVLine(line) {
        const result = [];
        let current = '';
        let inQuotes = false;

        for (let i = 0; i < line.length; i++) {
            const char = line[i];
            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                result.push(current.trim());
                current = '';
            } else {
                current += char;
            }
        }
        result.push(current.trim());
        return result;
    },

    showMappingStep(filename) {
        document.getElementById('import-step-1').classList.add('hidden');
        const step2 = document.getElementById('import-step-2');
        step2.classList.remove('hidden');

        const crmFields = [
            { key: 'org_name', label: 'Organization Name', required: true },
            { key: 'ein', label: 'EIN' },
            { key: 'phone', label: 'Phone' },
            { key: 'email', label: 'Email' },
            { key: 'website', label: 'Website' },
            { key: 'contact_name', label: 'Contact Name' },
            { key: 'contact_title', label: 'Contact Title' },
            { key: 'linkedin_url', label: 'LinkedIn URL' },
            { key: 'tier', label: 'Tier' },
            { key: 'city', label: 'City' },
            { key: 'state', label: 'State' },
            { key: 'ntee_code', label: 'NTEE Code' },
            { key: 'annual_budget', label: 'Annual Budget' },
            { key: 'icp_score', label: 'ICP Score' },
            { key: 'notes', label: 'Notes' }
        ];

        // Auto-map based on common names
        this.autoMapColumns(crmFields);

        step2.innerHTML = `
            <div class="card">
                <h3>Source List Info</h3>
                <div class="form-group">
                    <label class="form-label">List Name *</label>
                    <input type="text" class="form-input" id="source-name"
                        value="${escapeHtml(filename.replace('.csv', ''))}"
                        placeholder="e.g., Dec 2025 Healthcare ICP 10">
                </div>
                <div class="form-group">
                    <label class="form-label">Criteria/Description</label>
                    <textarea class="form-input form-textarea" id="source-criteria"
                        placeholder="Why were these prospects selected?"></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">Default Segment</label>
                    <select class="form-input form-select" id="default-segment">
                        <option value="nonprofit">Nonprofit</option>
                        <option value="foundation">Foundation</option>
                        <option value="foundation_mgmt">Foundation Management</option>
                    </select>
                </div>
            </div>

            <div class="card mt-16">
                <h3>Map Columns</h3>
                <p class="text-muted mb-16">Match CSV columns to CRM fields</p>

                ${crmFields.map(f => `
                    <div class="form-group">
                        <label class="form-label">${f.label}${f.required ? ' *' : ''}</label>
                        <select class="form-input form-select column-mapping" data-field="${f.key}">
                            <option value="">-- Skip --</option>
                            ${this.csvData.headers.map(h => `
                                <option value="${escapeHtml(h)}" ${this.columnMapping[f.key] === h ? 'selected' : ''}>
                                    ${escapeHtml(h)}
                                </option>
                            `).join('')}
                        </select>
                    </div>
                `).join('')}
            </div>

            <div class="mt-16">
                <button class="btn btn-primary btn-block" id="preview-import-btn">
                    Preview Import (${this.csvData.rows.length} rows)
                </button>
            </div>
        `;

        document.getElementById('preview-import-btn').addEventListener('click', () => {
            this.collectMappings();
            this.showPreviewStep();
        });
    },

    autoMapColumns(crmFields) {
        const commonMappings = {
            'org_name': ['org_name', 'organization_name', 'organization', 'company', 'company_name', 'name'],
            'ein': ['ein', 'employer_id', 'tax_id'],
            'phone': ['phone', 'phone_number', 'tel', 'telephone'],
            'email': ['email', 'email_address', 'e-mail'],
            'website': ['website', 'web', 'url', 'site'],
            'contact_name': ['contact_name', 'contact', 'primary_contact', 'ceo_name'],
            'contact_title': ['contact_title', 'title', 'position'],
            'city': ['city'],
            'state': ['state', 'state_abbr'],
            'ntee_code': ['ntee_code', 'ntee'],
            'annual_budget': ['annual_budget', 'budget', 'revenue', 'total_revenue'],
            'icp_score': ['icp_score', 'icp', 'score'],
            'tier': ['tier', 'tier_level'],
            'linkedin_url': ['linkedin_url', 'linkedin'],
            'notes': ['notes', 'comments']
        };

        const lowerHeaders = this.csvData.headers.map(h => h.toLowerCase().replace(/[^a-z0-9]/g, '_'));

        for (const [crmField, aliases] of Object.entries(commonMappings)) {
            for (const alias of aliases) {
                const idx = lowerHeaders.indexOf(alias);
                if (idx !== -1) {
                    this.columnMapping[crmField] = this.csvData.headers[idx];
                    break;
                }
            }
        }
    },

    collectMappings() {
        document.querySelectorAll('.column-mapping').forEach(select => {
            const field = select.dataset.field;
            this.columnMapping[field] = select.value;
        });

        this.sourceName = document.getElementById('source-name').value;
        this.sourceCriteria = document.getElementById('source-criteria').value;
        this.defaultSegment = document.getElementById('default-segment').value;

        if (!this.sourceName.trim()) {
            showToast('Please enter a source list name', 'error');
            return false;
        }

        if (!this.columnMapping['org_name']) {
            showToast('Organization Name is required', 'error');
            return false;
        }

        return true;
    },

    showPreviewStep() {
        document.getElementById('import-step-2').classList.add('hidden');
        const step3 = document.getElementById('import-step-3');
        step3.classList.remove('hidden');

        // Transform data
        const prospects = this.csvData.rows.map(row => this.transformRow(row));

        // Show preview
        const previewRows = prospects.slice(0, 5);

        step3.innerHTML = `
            <div class="card">
                <h3>Preview</h3>
                <p class="text-muted mb-16">Importing ${prospects.length} prospects as "${escapeHtml(this.defaultSegment)}"</p>

                ${previewRows.map((p, i) => `
                    <div class="card" style="background: var(--gray-50)">
                        <div class="card-title">${i + 1}. ${escapeHtml(p.org_name)}</div>
                        <div class="card-meta">
                            ${p.phone ? 'Phone: ' + p.phone : ''}
                            ${p.email ? ' | Email: ' + p.email : ''}
                            ${p.contact_name ? ' | Contact: ' + p.contact_name : ''}
                        </div>
                    </div>
                `).join('')}

                ${prospects.length > 5 ? `<p class="text-muted text-center">... and ${prospects.length - 5} more</p>` : ''}
            </div>

            <div class="mt-16 flex gap-8">
                <button class="btn btn-secondary flex-1" id="back-to-mapping">Back</button>
                <button class="btn btn-success flex-1" id="confirm-import">Import All</button>
            </div>
        `;

        document.getElementById('back-to-mapping').addEventListener('click', () => {
            step3.classList.add('hidden');
            document.getElementById('import-step-2').classList.remove('hidden');
        });

        document.getElementById('confirm-import').addEventListener('click', () => {
            this.executeImport(prospects);
        });
    },

    transformRow(row) {
        const prospect = {
            segment: this.defaultSegment,
            status: 'not_contacted'
        };

        for (const [crmField, csvColumn] of Object.entries(this.columnMapping)) {
            if (csvColumn && row[csvColumn]) {
                let value = row[csvColumn].trim();

                // Type conversions
                if (['tier', 'icp_score'].includes(crmField)) {
                    value = parseInt(value) || null;
                }
                if (crmField === 'annual_budget') {
                    value = parseInt(value.replace(/[^0-9]/g, '')) || null;
                }

                if (value) prospect[crmField] = value;
            }
        }

        return prospect;
    },

    async executeImport(prospects) {
        showLoading();

        try {
            // Create source list first
            const sourceList = await API.createSourceList({
                name: this.sourceName,
                criteria: this.sourceCriteria,
                file_origin: 'CSV Import',
                record_count: prospects.length,
                segment: this.defaultSegment
            });

            const sourceListId = sourceList[0].id;

            // Add source_list_id to all prospects
            prospects.forEach(p => p.source_list_id = sourceListId);

            // Bulk insert prospects
            await API.bulkCreateProspects(prospects);

            hideLoading();
            showToast(`Imported ${prospects.length} prospects!`, 'success');

            // Reset and go to queue
            this.csvData = null;
            this.columnMapping = {};
            navigateTo('queue');

        } catch (error) {
            hideLoading();
            console.error('Import failed:', error);
            showToast('Import failed: ' + error.message, 'error');
        }
    }
};
