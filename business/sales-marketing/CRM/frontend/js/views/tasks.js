// Tasks View
// Shows pending follow-ups and tasks

const TasksView = {
    tasks: [],

    async render() {
        const container = document.getElementById('app');
        container.innerHTML = `
            <div class="view-header">
                <h1>Tasks</h1>
                <button class="btn btn-primary btn-small" id="add-task-btn">+ Add Task</button>
            </div>

            <div id="tasks-list">
                <div class="loading-inline">Loading...</div>
            </div>
        `;

        document.getElementById('add-task-btn').addEventListener('click', () => {
            showAddTaskModal();
        });

        await this.loadTasks();
    },

    async loadTasks() {
        try {
            this.tasks = await API.getAllPendingTasks();
            this.renderList();
        } catch (error) {
            console.error('Failed to load tasks:', error);
            showToast('Failed to load tasks', 'error');
        }
    },

    renderList() {
        const listEl = document.getElementById('tasks-list');
        const today = new Date().toISOString().split('T')[0];

        if (this.tasks.length === 0) {
            listEl.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">&#9745;</div>
                    <div class="empty-state-title">All Caught Up!</div>
                    <p>No pending tasks. Great work!</p>
                </div>
            `;
            return;
        }

        // Group by due date
        const overdue = this.tasks.filter(t => t.due_date < today);
        const todayTasks = this.tasks.filter(t => t.due_date === today);
        const upcoming = this.tasks.filter(t => t.due_date > today);

        let html = '';

        if (overdue.length > 0) {
            html += `<h3 class="text-muted mb-16" style="color: var(--danger)">Overdue (${overdue.length})</h3>`;
            html += overdue.map(t => this.renderTask(t, true)).join('');
        }

        if (todayTasks.length > 0) {
            html += `<h3 class="text-muted mb-16 mt-16">Today (${todayTasks.length})</h3>`;
            html += todayTasks.map(t => this.renderTask(t)).join('');
        }

        if (upcoming.length > 0) {
            html += `<h3 class="text-muted mb-16 mt-16">Upcoming (${upcoming.length})</h3>`;
            html += upcoming.map(t => this.renderTask(t)).join('');
        }

        listEl.innerHTML = html;

        // Attach handlers
        listEl.querySelectorAll('.btn-complete-task').forEach(btn => {
            btn.addEventListener('click', () => this.completeTask(btn.dataset.id));
        });

        listEl.querySelectorAll('.task-prospect-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                showProspectDetail(link.dataset.id);
            });
        });
    },

    renderTask(task, isOverdue = false) {
        const typeIcons = {
            'call': '&#128222;',
            'email': '&#128231;',
            'meeting': '&#128100;',
            'other': '&#128203;'
        };

        const prospect = task.prospects || {};

        return `
            <div class="card" style="${isOverdue ? 'border-left: 3px solid var(--danger)' : ''}">
                <div class="card-header">
                    <div>
                        <div class="card-title">
                            ${typeIcons[task.type] || ''} ${escapeHtml(task.description || `Follow up with ${prospect.org_name}`)}
                        </div>
                        <div class="card-subtitle">
                            <a href="#" class="task-prospect-link" data-id="${task.prospect_id}" style="color: var(--primary)">
                                ${escapeHtml(prospect.org_name || 'Unknown')}
                            </a>
                            ${prospect.contact_name ? ' - ' + escapeHtml(prospect.contact_name) : ''}
                        </div>
                    </div>
                    <button class="btn btn-success btn-small btn-complete-task" data-id="${task.id}">
                        Done
                    </button>
                </div>
                <div class="card-meta">
                    Due: ${formatDate(task.due_date)}
                    ${prospect.phone ? ` | &#128222; <a href="tel:${prospect.phone}">${formatPhone(prospect.phone)}</a>` : ''}
                </div>
            </div>
        `;
    },

    async completeTask(id) {
        try {
            await API.completeTask(id);
            showToast('Task completed!', 'success');

            // Remove from UI
            this.tasks = this.tasks.filter(t => t.id !== parseInt(id));
            this.renderList();
        } catch (error) {
            console.error('Failed to complete task:', error);
            showToast('Failed to complete task', 'error');
        }
    }
};

function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr + 'T00:00:00');
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.getTime() === today.getTime()) return 'Today';
    if (date.getTime() === tomorrow.getTime()) return 'Tomorrow';

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}
