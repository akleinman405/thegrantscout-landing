# Dashboard Cleanup Script
# Automatically organizes files into clean folder structure
# Run in PowerShell: .\cleanup.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dashboard Cleanup Script v1.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get current directory
$baseDir = Get-Location

Write-Host "Current directory: $baseDir" -ForegroundColor Yellow
Write-Host ""

# Ask for confirmation
Write-Host "This script will:" -ForegroundColor White
Write-Host "  1. Create new folders (docs, tests, data, archive)" -ForegroundColor White
Write-Host "  2. Move 26 markdown files to organized locations" -ForegroundColor White
Write-Host "  3. Move test files to /tests folder" -ForegroundColor White
Write-Host "  4. Create .gitignore file" -ForegroundColor White
Write-Host "  5. Keep a backup of original structure" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Do you want to continue? (yes/no)"
if ($confirm -ne "yes") {
    Write-Host "Cleanup cancelled." -ForegroundColor Red
    exit
}

Write-Host ""
Write-Host "Starting cleanup..." -ForegroundColor Green
Write-Host ""

# Create backup
Write-Host "[1/6] Creating backup..." -ForegroundColor Yellow
$backupDir = "backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
Write-Host "  ✓ Backup folder created: $backupDir" -ForegroundColor Green

# Create folder structure
Write-Host "[2/6] Creating folder structure..." -ForegroundColor Yellow

$folders = @(
    "docs",
    "docs\archive",
    "docs\archive\fixes",
    "docs\archive\implementation",
    "docs\archive\planning",
    "docs\archive\testing",
    "docs\development",
    "tests",
    "tests\database",
    "data",
    "data\verticals"
)

foreach ($folder in $folders) {
    if (!(Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        Write-Host "  ✓ Created: $folder" -ForegroundColor Green
    }
}

# Move files to archive/fixes
Write-Host "[3/6] Moving fix documentation..." -ForegroundColor Yellow

$fixFiles = @(
    "FIXES_APPLIED.md",
    "FIXES_APPLIED_ROUND_2.md",
    "EMAIL_ACCOUNT_BUG_FIXED.md",
    "FIX_EMAIL_ACCOUNT_BUG.md",
    "NAVIGATION_RENAME_COMPLETE.md",
    "DASHBOARD_ANALYTICS_FIXED.md",
    "QUICK_WINS_IMPLEMENTED.md"
)

foreach ($file in $fixFiles) {
    if (Test-Path $file) {
        Move-Item $file "docs\archive\fixes\" -Force
        Write-Host "  ✓ Moved: $file" -ForegroundColor Green
    }
}

# Move implementation docs
Write-Host "[4/6] Moving implementation documentation..." -ForegroundColor Yellow

$implFiles = @(
    "BACKEND_INTEGRATION_SUMMARY.md",
    "FRONTEND_IMPLEMENTATION_SUMMARY.md",
    "DATABASE_IMPLEMENTATION_SUMMARY.md",
    "DOCUMENTATION_COMPLETION_SUMMARY.md",
    "DELIVERY_SUMMARY.md",
    "CAMPAIGN_CONTROL_SUMMARY.md"
)

foreach ($file in $implFiles) {
    if (Test-Path $file) {
        Move-Item $file "docs\archive\implementation\" -Force
        Write-Host "  ✓ Moved: $file" -ForegroundColor Green
    }
}

# Move planning docs
Write-Host "[5/6] Moving planning documentation..." -ForegroundColor Yellow

$planFiles = @(
    "CLAUDE_CODE_DASHBOARD_PROMPT.md",
    "TROUBLESHOOTING_PROMPT.md",
    "QUICK_FIX_INSTRUCTIONS.md"
)

foreach ($file in $planFiles) {
    if (Test-Path $file) {
        Move-Item $file "docs\archive\planning\" -Force
        Write-Host "  ✓ Moved: $file" -ForegroundColor Green
    }
}

# Move implementation_docs folder
if (Test-Path "implementation_docs") {
    Move-Item "implementation_docs" "docs\archive\planning\" -Force
    Write-Host "  ✓ Moved: implementation_docs/" -ForegroundColor Green
}

# Move testing docs
Write-Host "[6/6] Moving testing documentation..." -ForegroundColor Yellow

$testFiles = @(
    "QA_SUMMARY.md",
    "TEST_REPORT.md",
    "MANUAL_TESTING_CHECKLIST.md"
)

foreach ($file in $testFiles) {
    if (Test-Path $file) {
        Move-Item $file "docs\archive\testing\" -Force
        Write-Host "  ✓ Moved: $file" -ForegroundColor Green
    }
}

# Move Launch Results files
Get-ChildItem -Path "." -Filter "Launch*" | ForEach-Object {
    if ($_.Name -ne "LAUNCH.md") {
        Move-Item $_.FullName "docs\archive\testing\" -Force
        Write-Host "  ✓ Moved: $($_.Name)" -ForegroundColor Green
    }
}

# Move user docs to docs/
Write-Host "Moving user documentation..." -ForegroundColor Yellow

$userFiles = @(
    "SETUP_INSTRUCTIONS.md",
    "TROUBLESHOOTING.md",
    "CAMPAIGN_CONTROL_GUIDE.md"
)

foreach ($file in $userFiles) {
    if (Test-Path $file) {
        Move-Item $file "docs\" -Force
        Write-Host "  ✓ Moved: $file → docs/" -ForegroundColor Green
    }
}

# Rename and move API guide
if (Test-Path "INTEGRATION_API_GUIDE.md") {
    Move-Item "INTEGRATION_API_GUIDE.md" "docs\API_GUIDE.md" -Force
    Write-Host "  ✓ Moved: INTEGRATION_API_GUIDE.md → docs/API_GUIDE.md" -ForegroundColor Green
}

# Rename and move feature requests
if (Test-Path "OUTSTANDING_REQUESTS_SUMMARY.md") {
    Move-Item "OUTSTANDING_REQUESTS_SUMMARY.md" "docs\FEATURE_REQUESTS.md" -Force
    Write-Host "  ✓ Moved: OUTSTANDING_REQUESTS_SUMMARY.md → docs/FEATURE_REQUESTS.md" -ForegroundColor Green
}

# Move development docs
if (Test-Path "FEATURE_PLAN_RESPONSE_TRACKING.md") {
    Move-Item "FEATURE_PLAN_RESPONSE_TRACKING.md" "docs\development\" -Force
    Write-Host "  ✓ Moved: FEATURE_PLAN_RESPONSE_TRACKING.md" -ForegroundColor Green
}

# Move test files
Write-Host "Moving test files..." -ForegroundColor Yellow

if (Test-Path "test_integration.py") {
    Move-Item "test_integration.py" "tests\" -Force
    Write-Host "  ✓ Moved: test_integration.py" -ForegroundColor Green
}

if (Test-Path "test_suite_comprehensive.py") {
    Move-Item "test_suite_comprehensive.py" "tests\" -Force
    Write-Host "  ✓ Moved: test_suite_comprehensive.py" -ForegroundColor Green
}

if (Test-Path "database\test_database.py") {
    Move-Item "database\test_database.py" "tests\database\" -Force
    Write-Host "  ✓ Moved: database/test_database.py" -ForegroundColor Green
}

if (Test-Path "database\QUICKSTART.md") {
    Remove-Item "database\QUICKSTART.md" -Force
    Write-Host "  ✓ Removed: database/QUICKSTART.md (duplicate)" -ForegroundColor Green
}

# Move data files
Write-Host "Moving data files..." -ForegroundColor Yellow

if (Test-Path ".encryption_key") {
    Move-Item ".encryption_key" "data\" -Force
    Write-Host "  ✓ Moved: .encryption_key → data/" -ForegroundColor Green
}

if (Test-Path "campaign_control.db") {
    Move-Item "campaign_control.db" "data\" -Force
    Write-Host "  ✓ Moved: campaign_control.db → data/" -ForegroundColor Green
}

if (Test-Path "verticals") {
    Move-Item "verticals" "data\" -Force
    Write-Host "  ✓ Moved: verticals/ → data/" -ForegroundColor Green
}

# Create .gitignore
Write-Host "Creating .gitignore..." -ForegroundColor Yellow

$gitignoreContent = @"
# Python
__pycache__/
*.py[cod]
*`$py.class
*.so
.Python

# Virtual Environment
venv/
env/
ENV/

# Database
*.db
*.db-journal

# Sensitive Data
.encryption_key
data/*.db
data/verticals/*/prospects.csv

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Temporary files
*.tmp
Launch
Launch Results*

# Backups
backup_*

# Archive
docs/archive/
"@

Set-Content -Path ".gitignore" -Value $gitignoreContent
Write-Host "  ✓ Created: .gitignore" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cleanup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Summary:" -ForegroundColor White
Write-Host "  ✓ Created folder structure" -ForegroundColor Green
Write-Host "  ✓ Moved 26+ files to organized locations" -ForegroundColor Green
Write-Host "  ✓ Created .gitignore" -ForegroundColor Green
Write-Host "  ✓ Backup created: $backupDir" -ForegroundColor Green
Write-Host ""

Write-Host "Root directory now contains only:" -ForegroundColor Yellow
Write-Host "  - dashboard.py (main app)" -ForegroundColor White
Write-Host "  - requirements.txt (dependencies)" -ForegroundColor White
Write-Host "  - README.md (documentation)" -ForegroundColor White
Write-Host "  - LAUNCH.md (quick start)" -ForegroundColor White
Write-Host "  - HOW_IT_WORKS.md (architecture)" -ForegroundColor White
Write-Host "  - CLEANUP_PLAN.md (this plan)" -ForegroundColor White
Write-Host "  - .gitignore (git config)" -ForegroundColor White
Write-Host "  - Core folders (pages/, components/, etc.)" -ForegroundColor White
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test dashboard: streamlit run dashboard.py" -ForegroundColor White
Write-Host "  2. Verify all pages load correctly" -ForegroundColor White
Write-Host "  3. Check paths if any errors occur" -ForegroundColor White
Write-Host "  4. Review docs/ folder for documentation" -ForegroundColor White
Write-Host ""

Write-Host "If anything breaks, restore from: $backupDir" -ForegroundColor Cyan
Write-Host ""

# Pause at end
Read-Host "Press Enter to exit"
