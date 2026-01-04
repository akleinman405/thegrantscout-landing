// Supabase Configuration
// Project: akleinman405's Project (used for TGS CRM)

const SUPABASE_URL = 'https://qisbqmwtfzeiffgtlzpk.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFpc2JxbXd0ZnplaWZmZ3RsenBrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjY3MTMzMTYsImV4cCI6MjA4MjI4OTMxNn0.jX4J13DNMFy1AXUtG0UBdCU4pnw3NBL1cwT-oCUlxOo';

// App Configuration
const APP_CONFIG = {
    pageSize: 25,
    toastDuration: 3000,
    defaultSegment: 'all',
    defaultStatus: 'all'
};

// Check if configured
function isConfigured() {
    return SUPABASE_URL !== 'YOUR_SUPABASE_URL' && SUPABASE_ANON_KEY !== 'YOUR_ANON_KEY';
}
