// Search View
// Search prospects by name, phone, EIN, etc.

const SearchView = {
    results: [],
    searchTimeout: null,

    async render() {
        const container = document.getElementById('app');
        container.innerHTML = `
            <div class="view-header">
                <h1>Search</h1>
            </div>

            <div class="search-container">
                <span class="search-icon">&#128269;</span>
                <input type="text" class="search-input" id="search-input"
                    placeholder="Search by name, phone, or EIN..."
                    autocomplete="off" autocapitalize="off">
            </div>

            <div id="search-results"></div>
        `;

        const input = document.getElementById('search-input');
        input.addEventListener('input', (e) => this.handleSearch(e.target.value));
        input.focus();
    },

    handleSearch(query) {
        // Debounce search
        clearTimeout(this.searchTimeout);

        if (query.length < 2) {
            document.getElementById('search-results').innerHTML = `
                <div class="text-center text-muted" style="padding: 24px">
                    Enter at least 2 characters to search
                </div>
            `;
            return;
        }

        document.getElementById('search-results').innerHTML = `
            <div class="text-center text-muted" style="padding: 24px">
                Searching...
            </div>
        `;

        this.searchTimeout = setTimeout(() => this.doSearch(query), 300);
    },

    async doSearch(query) {
        try {
            this.results = await API.searchProspects(query);
            this.renderResults(query);
        } catch (error) {
            console.error('Search failed:', error);
            showToast('Search failed', 'error');
        }
    },

    renderResults(query) {
        const container = document.getElementById('search-results');

        if (this.results.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">&#128269;</div>
                    <div class="empty-state-title">No Results</div>
                    <p>No prospects match "${escapeHtml(query)}"</p>
                </div>
            `;
            return;
        }

        container.innerHTML = `
            <div class="text-muted mb-16">${this.results.length} result${this.results.length === 1 ? '' : 's'}</div>
            ${this.results.map(p => this.renderResult(p, query)).join('')}
        `;

        // Attach handlers
        container.querySelectorAll('.prospect-card').forEach(card => {
            card.addEventListener('click', () => showProspectDetail(card.dataset.id));
        });
    },

    renderResult(prospect, query) {
        return `
            <div class="card prospect-card" data-id="${prospect.id}">
                <div class="card-header">
                    <div>
                        <div class="card-title">${this.highlight(prospect.org_name, query)}</div>
                        ${prospect.contact_name ? `<div class="card-subtitle">${this.highlight(prospect.contact_name, query)}</div>` : ''}
                    </div>
                    <div>
                        <span class="badge badge-${prospect.status}">${formatStatus(prospect.status)}</span>
                        <span class="badge badge-${prospect.segment}">${formatSegment(prospect.segment)}</span>
                    </div>
                </div>
                <div class="card-meta">
                    ${prospect.phone ? `&#128222; ${this.highlight(formatPhone(prospect.phone), query)}` : ''}
                    ${prospect.ein ? ` | EIN: ${this.highlight(prospect.ein, query)}` : ''}
                    ${prospect.city && prospect.state ? ` | ${prospect.city}, ${prospect.state}` : ''}
                </div>
            </div>
        `;
    },

    highlight(text, query) {
        if (!text || !query) return escapeHtml(text);
        const escaped = escapeHtml(text);
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        return escaped.replace(regex, '<mark>$1</mark>');
    }
};

function formatStatus(status) {
    const labels = {
        'not_contacted': 'Not Contacted',
        'contacted': 'Contacted',
        'interested': 'Interested',
        'not_interested': 'Not Interested',
        'converted': 'Converted'
    };
    return labels[status] || status;
}
