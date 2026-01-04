# TheGrantScout Website - Quick Commands Reference

Fast reference for common development, testing, and deployment commands.

---

## Table of Contents

- [Development Commands](#development-commands)
- [Testing Commands](#testing-commands)
- [Production Build](#production-build)
- [Troubleshooting Commands](#troubleshooting-commands)
- [Git Commands](#git-commands)
- [Windows-Specific Tips](#windows-specific-tips)

---

## Development Commands

### Start Development Server

```cmd
npm run dev
```
- Starts local server at http://localhost:3000
- Auto-reloads when you save files
- Shows compile errors in console
- Leave terminal window open

**Alternative Port:**
```cmd
npm run dev -- -p 3001
```
Use if port 3000 is busy (opens at http://localhost:3001)

### Stop Development Server

In the Command Prompt window:
- Press `Ctrl + C`
- Type `Y` if prompted
- Press Enter

---

## Testing Commands

### Install Dependencies

```cmd
npm install
```
- Run once when setting up project
- Run again if package.json changes
- Run if node_modules folder is deleted
- Takes 2-5 minutes

### Clean Install (Fresh Start)

```cmd
npm ci
```
- Faster than `npm install`
- Uses exact versions from package-lock.json
- Deletes node_modules first
- Good for fixing dependency issues

### Check for Errors (Lint)

```cmd
npm run lint
```
- Checks code for common mistakes
- Reports errors and warnings
- Should show no errors before deploying

### Fix Linting Errors Automatically

```cmd
npm run lint -- --fix
```
- Automatically fixes simple issues
- Still need to fix complex ones manually

### Type Check (TypeScript)

```cmd
npx tsc --noEmit
```
- Checks for TypeScript type errors
- Doesn't create any files
- Should show no errors before deploying

---

## Production Build

### Build for Production

```cmd
npm run build
```
- Creates optimized production version
- Output goes to `.next` folder
- Takes 1-3 minutes
- Run this before deploying
- Should complete with no errors

**Successful build shows:**
```
Route (app)                Size     First Load JS
┌ ○ /                      5 kB       85 kB
└ ○ /404                   142 B      77 kB

○  (Static)  prerendered as static content

✓ Compiled successfully
```

### Start Production Server Locally

```cmd
npm start
```
- Runs the production build locally
- Must run `npm run build` first
- Test this before deploying
- Opens at http://localhost:3000

### Static Export (for non-Vercel hosting)

```cmd
npm run build
```
Then find static files in the `out` folder (if configured for static export).

---

## Troubleshooting Commands

### Clear Next.js Cache

```cmd
npx next clean
```
- Deletes `.next` folder
- Clears build cache
- Use if seeing strange build errors
- Then run `npm run dev` or `npm run build` again

### Clear npm Cache

```cmd
npm cache clean --force
```
- Clears npm's download cache
- Use if getting "EINTEGRITY" errors
- Won't hurt anything

### Delete and Reinstall Everything

```cmd
rmdir /s /q node_modules
del package-lock.json
npm install
```
- Windows commands to start fresh
- Deletes all dependencies
- Reinstalls from scratch
- Last resort for dependency issues
- Takes 5+ minutes

**Step-by-step explanation:**
1. `rmdir /s /q node_modules` - Delete node_modules folder
2. `del package-lock.json` - Delete lock file
3. `npm install` - Reinstall everything

### Check Node and npm Versions

```cmd
node --version
npm --version
```
- Shows installed versions
- Should see v18+ for Node
- Should see v9+ for npm

### Update npm

```cmd
npm install -g npm@latest
```
- Updates npm to latest version
- May require admin privileges
- Restart terminal after

### Kill Process on Port 3000

```cmd
netstat -ano | findstr :3000
taskkill /PID [NUMBER] /F
```
Replace `[NUMBER]` with the PID from first command.

**Example:**
```cmd
netstat -ano | findstr :3000
```
Output: `TCP  0.0.0.0:3000  0.0.0.0:0  LISTENING  1234`

Then:
```cmd
taskkill /PID 1234 /F
```

---

## Git Commands

### First Time Setup

```cmd
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```
- Run once on new computer
- Sets your identity for commits

### Initialize Git Repository

```cmd
git init
```
- Creates new Git repository
- Run once in project folder
- Creates hidden `.git` folder

### Check Status

```cmd
git status
```
- Shows changed files
- Shows untracked files
- Shows what's staged for commit

### Add Files to Staging

```cmd
git add .
```
- Stages all changed files
- Ready to commit

**Add specific file:**
```cmd
git add src/app/page.tsx
```

### Commit Changes

```cmd
git commit -m "Your descriptive message here"
```

**Good commit messages:**
- "Add hero section with CTA buttons"
- "Fix mobile responsive layout on pricing section"
- "Update FAQ content with new questions"
- "Optimize images for faster loading"

**Bad commit messages:**
- "Update stuff"
- "Fix"
- "Changes"

### Push to GitHub

```cmd
git push
```
Or first time:
```cmd
git push -u origin main
```

### Pull Latest Changes

```cmd
git pull
```
- Gets latest changes from GitHub
- Use if collaborating with others

### View Commit History

```cmd
git log --oneline
```
- Shows recent commits
- Press `q` to exit

---

## Windows-Specific Tips

### Navigate to Project Folder

**Long path with spaces:**
```cmd
cd "C:\Business Factory (Research) 11-1-2025\01_VALIDATED_IDEAS\TIER_1_BOOTSTRAPPED\IDEA_062_Grant_Alerts\TheGrantScout\3. Website\thegrantscout-landing"
```

**Tip:** Use quotes around paths with spaces!

**Shortcut:**
1. Open folder in File Explorer
2. Click in address bar
3. Type `cmd` and press Enter
4. Command Prompt opens in that folder!

### Copy File Paths

In File Explorer:
1. Hold `Shift` key
2. Right-click file or folder
3. Click "Copy as path"
4. Path is copied with quotes

### List Files

```cmd
dir
```
- Shows files in current folder
- Like `ls` on Mac/Linux

### Change Drive

```cmd
D:
```
- Switches to D: drive
- Replace with any drive letter (C:, E:, etc.)

### Clear Terminal

```cmd
cls
```
- Clears the screen
- Fresh start

### Run as Administrator

If you get permission errors:
1. Close Command Prompt
2. Press Windows key
3. Type "cmd"
4. Right-click "Command Prompt"
5. Select "Run as administrator"
6. Navigate to project folder again

---

## Common Command Sequences

### Starting a Fresh Work Session

```cmd
cd "C:\Business Factory (Research) 11-1-2025\01_VALIDATED_IDEAS\TIER_1_BOOTSTRAPPED\IDEA_062_Grant_Alerts\TheGrantScout\3. Website\thegrantscout-landing"
npm run dev
```
Then open http://localhost:3000

### Saving Your Work

```cmd
git add .
git commit -m "Describe what you changed"
git push
```

### Preparing for Deployment

```cmd
npm run lint
npm run build
npm start
```
Then test at http://localhost:3000

### Fixing Everything (Nuclear Option)

```cmd
Ctrl + C
rmdir /s /q node_modules
rmdir /s /q .next
del package-lock.json
npm cache clean --force
npm install
npm run dev
```

---

## VS Code Shortcuts

If using Visual Studio Code:

### Open Integrated Terminal

- ``Ctrl + ` `` (backtick key)
- Or: Terminal menu → New Terminal

### Multiple Terminals

- Click `+` in terminal panel
- Switch between terminals in dropdown

### Format Code

- `Shift + Alt + F` - Format current file
- Requires Prettier extension

### Search Project

- `Ctrl + Shift + F` - Search all files
- `Ctrl + F` - Search current file

### Open File Quickly

- `Ctrl + P` - Quick file open
- Start typing filename
- Press Enter to open

### Save All Files

- `Ctrl + K, S` - Save all open files
- Press `Ctrl + K`, release, then press `S`

---

## Package Manager Alternatives

### Using Yarn Instead of npm

If you prefer Yarn:

**Install Yarn:**
```cmd
npm install -g yarn
```

**Commands:**
```cmd
yarn              # Install dependencies
yarn dev          # Start dev server
yarn build        # Build for production
yarn lint         # Lint code
```

### Using pnpm Instead of npm

If you prefer pnpm (faster):

**Install pnpm:**
```cmd
npm install -g pnpm
```

**Commands:**
```cmd
pnpm install      # Install dependencies
pnpm dev          # Start dev server
pnpm build        # Build for production
pnpm lint         # Lint code
```

---

## Environment Variables

### Create .env.local File

In project root, create file named `.env.local`:

```
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_API_URL=https://api.example.com
```

**Important:**
- Never commit `.env.local` to Git
- Add to `.gitignore`
- Variables starting with `NEXT_PUBLIC_` are visible in browser
- Other variables are server-side only

### Use in Code

```javascript
const gaId = process.env.NEXT_PUBLIC_GA_ID
```

---

## Performance Testing

### Lighthouse Audit (Chrome Only)

1. Open site in Chrome
2. Press `F12`
3. Click "Lighthouse" tab
4. Click "Generate report"

**Or via Command Line:**
```cmd
npm install -g lighthouse
lighthouse http://localhost:3000
```

### Check Bundle Size

```cmd
npm run build
```
Look for size report in output.

**Analyze Bundle:**
```cmd
npm install -g webpack-bundle-analyzer
npm run build
npx webpack-bundle-analyzer .next/static/webpack/*.json
```

---

## Helpful npm Packages

### Install Additional Package

```cmd
npm install package-name
```

**Examples:**
```cmd
npm install react-icons          # Icon library
npm install framer-motion        # Animations
npm install @heroicons/react     # Hero icons
```

### Install as Dev Dependency

```cmd
npm install --save-dev package-name
```

**Examples:**
```cmd
npm install --save-dev prettier  # Code formatter
npm install --save-dev eslint    # Linter
```

### Uninstall Package

```cmd
npm uninstall package-name
```

### Update All Packages

```cmd
npm update
```
**Or for major updates:**
```cmd
npx npm-check-updates -u
npm install
```

---

## Quick Troubleshooting

### "Command not found" or "is not recognized"

**Problem:** Node/npm not in PATH

**Fix:**
1. Restart computer
2. Reinstall Node.js
3. Check "Add to PATH" during installation

### "Port 3000 already in use"

**Fix:**
```cmd
npm run dev -- -p 3001
```
Or kill process (see above)

### "Permission denied" or "EPERM"

**Fix:**
1. Run Command Prompt as Administrator
2. Or disable antivirus temporarily

### Build failing

**Fix:**
```cmd
npx next clean
npm run build
```

### Changes not showing in browser

**Fix:**
- Hard refresh: `Ctrl + Shift + R`
- Or restart dev server: `Ctrl + C` then `npm run dev`

### npm install fails

**Fix:**
```cmd
npm cache clean --force
rmdir /s /q node_modules
del package-lock.json
npm install
```

---

## Keyboard Shortcuts

### Command Prompt

- `Ctrl + C` - Stop current process
- `Ctrl + V` - Paste (may need to enable in properties)
- `Tab` - Auto-complete folder/file names
- `Up Arrow` - Previous command
- `Down Arrow` - Next command

### Browser (Testing)

- `F12` - Open Developer Tools
- `Ctrl + Shift + I` - Open Developer Tools (alternative)
- `Ctrl + Shift + M` - Toggle device toolbar (responsive mode)
- `Ctrl + Shift + R` - Hard refresh (clear cache)
- `Ctrl + Shift + Delete` - Clear browsing data
- `F5` - Refresh page
- `Ctrl + +` - Zoom in
- `Ctrl + -` - Zoom out
- `Ctrl + 0` - Reset zoom

---

## Getting Help

### Check Documentation

**Next.js:**
- https://nextjs.org/docs

**Tailwind CSS:**
- https://tailwindcss.com/docs

**React:**
- https://react.dev

### Search for Errors

Copy exact error message and Google it with "Next.js" or "React"

**Good search:**
- "Next.js Error: listen EADDRINUSE :::3000"
- "npm install EINTEGRITY error"

### Common Resources

- Stack Overflow: https://stackoverflow.com
- GitHub Issues: Search the Next.js repo
- Vercel Discord: https://discord.gg/vercel

---

## Daily Workflow

### Morning Startup

```cmd
cd [project-folder]
git pull
npm install    # Only if package.json changed
npm run dev
```

### Making Changes

1. Edit files in VS Code
2. Save (Ctrl + S)
3. Check browser (auto-refreshes)
4. Check terminal for errors

### End of Day

```cmd
git add .
git commit -m "Describe today's work"
git push
```

Then press `Ctrl + C` to stop dev server.

---

## Summary of Most-Used Commands

**Essential Commands (use daily):**
```cmd
npm run dev       # Start development
npm run build     # Build for production
git status        # Check what changed
git add .         # Stage changes
git commit -m ""  # Commit changes
git push          # Push to GitHub
```

**Troubleshooting Commands (use when needed):**
```cmd
npx next clean            # Clear Next.js cache
npm cache clean --force   # Clear npm cache
npm install              # Reinstall dependencies
```

**Testing Commands (use before deploying):**
```cmd
npm run lint     # Check for errors
npm run build    # Build production version
npm start        # Test production build
```

---

## Cheat Sheet Printable

```
===========================================
THEGRANTSCOUT - QUICK COMMAND REFERENCE
===========================================

DEVELOPMENT:
  npm run dev         Start dev server
  Ctrl + C            Stop dev server

BUILD:
  npm run build       Build production
  npm start           Run production locally

GIT:
  git status          Check changes
  git add .           Stage all files
  git commit -m "…"   Commit with message
  git push            Push to GitHub

FIX ISSUES:
  npx next clean      Clear Next cache
  npm install         Reinstall dependencies

NAVIGATE:
  cd [folder]         Change directory
  dir                 List files
  cls                 Clear screen

BROWSER:
  F12                 Dev Tools
  Ctrl+Shift+M        Mobile view
  Ctrl+Shift+R        Hard refresh

===========================================
```

---

**Print this page for quick reference at your desk!**

**Questions?** See full guides:
- `WINDOWS_SETUP_GUIDE.md` - Installation help
- `TESTING_CHECKLIST.md` - What to test
- `DEPLOYMENT_GUIDE.md` - How to deploy

---

**Last Updated:** 2025-11-30
