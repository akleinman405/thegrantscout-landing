// Main App - Navigation and Global State
const APP_VERSION = '2026.01.02.2'; // For cache debugging

// Current view reference
let currentView = null;

// View registry
const views = {
    queue: QueueView,
    prospects: ProspectsView,
    import: ImportView,
    dashboard: DashboardView,
    campaigns: CampaignsView
};

// Initialize app
document.addEventListener('DOMContentLoaded', async () => {
    // Check configuration
    if (!isConfigured()) {
        showConfigError();
        return;
    }

    // Set up navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            navigateTo(btn.dataset.view);
        });
    });

    // Handle browser back button
    window.addEventListener('popstate', (e) => {
        if (e.state && e.state.view) {
            navigateTo(e.state.view, false);
        }
    });

    // Initialize timer (floating clock in/out)
    await TimerView.init();

    // Initial view
    const hash = window.location.hash.slice(1) || 'queue';
    navigateTo(hash);
});

// Navigation function
function navigateTo(viewName, pushState = true) {
    const view = views[viewName];
    if (!view) {
        console.error(`Unknown view: ${viewName}`);
        return;
    }

    // Update nav active state
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === viewName);
    });

    // Update URL
    if (pushState) {
        history.pushState({ view: viewName }, '', `#${viewName}`);
    }

    // Render view
    currentView = view;
    view.render();
}

// Modal functions
function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

function showProspectDetail(id, queueList = null, currentIndex = null) {
    // Ensure id is a number
    const prospectId = parseInt(id);
    if (isNaN(prospectId)) {
        console.error('Invalid prospect ID:', id);
        showToast('Invalid prospect ID', 'error');
        return;
    }
    ProspectView.show(prospectId, queueList, currentIndex);
}

// Toast notifications
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;

    setTimeout(() => {
        toast.classList.add('hidden');
    }, APP_CONFIG.toastDuration);
}

// Loading overlay
function showLoading() {
    document.getElementById('loading').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

// Configuration error screen
function showConfigError() {
    document.getElementById('app').innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">&#9888;</div>
            <div class="empty-state-title">Configuration Required</div>
            <p>Please update <code>js/config.js</code> with your Supabase credentials:</p>
            <div class="card mt-16" style="text-align: left;">
                <pre style="font-size: 0.875rem; overflow-x: auto;">
const SUPABASE_URL = 'https://your-project.supabase.co';
const SUPABASE_ANON_KEY = 'your-anon-key';
                </pre>
            </div>
            <p class="mt-16">See <a href="CLI.md">CLI.md</a> for setup instructions.</p>
        </div>
    `;

    // Hide nav
    document.querySelector('.nav-bar').style.display = 'none';
}

// Global keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Escape closes modals
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal:not(.hidden)').forEach(modal => {
            modal.classList.add('hidden');
        });
    }

});

// Service Worker registration for PWA
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
        .then(reg => console.log('SW registered:', reg.scope))
        .catch(err => console.log('SW registration failed:', err));
}

// Prevent double-tap zoom on mobile
let lastTouchEnd = 0;
document.addEventListener('touchend', (e) => {
    const now = Date.now();
    if (now - lastTouchEnd <= 300) {
        e.preventDefault();
    }
    lastTouchEnd = now;
}, false);

// Handle visibility change (refresh data when tab becomes visible)
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && currentView && currentView.render) {
        // Optionally refresh data when returning to tab
        // currentView.render();
    }
});

console.log('TGS CRM initialized');
