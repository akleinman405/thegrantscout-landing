# TheGrantScout Website - Windows Setup Guide

Complete step-by-step guide for setting up the TheGrantScout website project on Windows.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Step-by-Step Installation](#step-by-step-installation)
3. [Project Setup](#project-setup)
4. [Running the Development Server](#running-the-development-server)
5. [Common Windows Issues](#common-windows-issues)
6. [Troubleshooting](#troubleshooting)
7. [Next Steps](#next-steps)

---

## Prerequisites

Before you begin, you'll need to install the following software on your Windows computer:

### 1. Node.js (Required)

Node.js is the JavaScript runtime that powers the website.

**Installation Steps:**

1. Visit https://nodejs.org in your web browser
2. Download the **LTS (Long Term Support)** version
   - Look for the big green button that says "Recommended For Most Users"
   - Current recommended version: 18.x or 20.x
3. Run the downloaded installer (`node-vXX.X.X-x64.msi`)
4. In the installer:
   - Click "Next" on the welcome screen
   - Accept the license agreement
   - Keep the default installation path: `C:\Program Files\nodejs\`
   - **Important**: Make sure "Add to PATH" is checked (it should be by default)
   - Click through and complete the installation
5. Restart your computer (this ensures PATH changes take effect)

**Verify Installation:**

1. Open Command Prompt:
   - Press `Windows Key + R`
   - Type `cmd` and press Enter
2. Type these commands one at a time:
   ```cmd
   node --version
   ```
   You should see something like: `v20.10.0`

   ```cmd
   npm --version
   ```
   You should see something like: `10.2.3`

If you see version numbers, you're good to go!

### 2. Code Editor (Recommended)

**Visual Studio Code** is the recommended editor for this project.

**Installation Steps:**

1. Visit https://code.visualstudio.com
2. Click "Download for Windows"
3. Run the installer
4. During installation:
   - Check "Add to PATH"
   - Check "Create a desktop icon"
   - Check "Add 'Open with Code' action to Windows Explorer context menu"
5. Complete the installation

**Useful VS Code Extensions:**

After installing VS Code, install these extensions:
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- Prettier - Code formatter
- ESLint

To install extensions:
1. Open VS Code
2. Click the Extensions icon on the left (or press `Ctrl+Shift+X`)
3. Search for each extension by name
4. Click "Install"

### 3. Git for Windows (Optional but Recommended)

Git helps you track changes to your code.

**Installation Steps:**

1. Visit https://git-scm.com/download/win
2. Download the installer
3. Run the installer
4. Use default options (just keep clicking "Next")
5. Finish the installation

**Verify Installation:**

Open Command Prompt and type:
```cmd
git --version
```
You should see something like: `git version 2.43.0.windows.1`

---

## Step-by-Step Installation

Now that you have the prerequisites, let's set up the project.

### Step 1: Open Command Prompt

1. Press `Windows Key + R`
2. Type `cmd` and press Enter

OR

1. Click the Start Menu
2. Type "Command Prompt"
3. Click "Command Prompt" when it appears

### Step 2: Navigate to the Project Directory

The project is located in a folder with spaces in the name, so we need to use quotes:

```cmd
cd "C:\Business Factory (Research) 11-1-2025\01_VALIDATED_IDEAS\TIER_1_BOOTSTRAPPED\IDEA_062_Grant_Alerts\TheGrantScout\3. Website"
```

**Tip**: You can also navigate using File Explorer:
1. Open File Explorer
2. Navigate to the folder listed above
3. Click in the address bar at the top
4. Type `cmd` and press Enter
   - This opens Command Prompt directly in that folder!

### Step 3: Verify You're in the Right Place

Type:
```cmd
dir
```

You should see files like:
- PROJECT_PLAN.md
- README.md
- docs (folder)
- src (folder)
- public (folder)

If you don't see these, double-check your path.

---

## Project Setup

### Option A: Starting Fresh (Template Clone)

If you're setting up for the first time and need to clone the template:

1. Make sure you're in the "3. Website" folder (see Step 2 above)

2. Clone the template:
   ```cmd
   git clone https://github.com/nexi-launch/finwise-landing-page.git thegrantscout-landing
   ```

3. Navigate into the new folder:
   ```cmd
   cd thegrantscout-landing
   ```

4. Install dependencies:
   ```cmd
   npm install
   ```

   This will take 2-5 minutes. You'll see a lot of text scrolling - that's normal!

   When it's done, you should see a message like:
   ```
   added 312 packages, and audited 313 packages in 2m
   ```

### Option B: Existing Project Setup

If the project files are already set up:

1. Navigate to the project folder:
   ```cmd
   cd "C:\Business Factory (Research) 11-1-2025\01_VALIDATED_IDEAS\TIER_1_BOOTSTRAPPED\IDEA_062_Grant_Alerts\TheGrantScout\3. Website\thegrantscout-landing"
   ```

2. Install dependencies:
   ```cmd
   npm install
   ```

---

## Running the Development Server

### Start the Server

In Command Prompt (make sure you're in the project folder):

```cmd
npm run dev
```

You should see output like:
```
> thegrantscout-landing@0.1.0 dev
> next dev

- ready started server on 0.0.0.0:3000, url: http://localhost:3000
- event compiled client and server successfully in 2.3s
```

### View the Website

1. Open your web browser (Chrome, Edge, or Firefox)
2. Go to: `http://localhost:3000`
3. You should see the website!

**Leave Command Prompt open** - closing it will stop the server.

### Making Changes

While the development server is running:
- Any changes you make to files will automatically update in the browser
- Just save your file and refresh the browser (or it may auto-refresh)

### Stopping the Server

When you're done working:
1. Go to the Command Prompt window
2. Press `Ctrl + C`
3. If asked "Terminate batch job (Y/N)?", type `Y` and press Enter

---

## Common Windows Issues

### Issue 1: "node is not recognized"

**Error Message:**
```
'node' is not recognized as an internal or external command
```

**Solution:**
1. Node.js is not installed or not in your PATH
2. Restart your computer (this is often all you need)
3. If still not working, reinstall Node.js and make sure "Add to PATH" is checked

**Verify PATH:**
1. Open Command Prompt
2. Type: `echo %PATH%`
3. Look for `C:\Program Files\nodejs\` in the output
4. If it's not there, reinstall Node.js

### Issue 2: "Access Denied" or Permission Errors

**Error Message:**
```
Error: EPERM: operation not permitted
```

**Solution 1 - Run as Administrator:**
1. Close Command Prompt
2. Right-click on Command Prompt
3. Select "Run as administrator"
4. Navigate to project folder again
5. Try `npm install` again

**Solution 2 - Antivirus/Security:**
1. Your antivirus may be blocking npm
2. Temporarily disable antivirus
3. Run `npm install`
4. Re-enable antivirus

### Issue 3: Long Path Names Error

**Error Message:**
```
Error: ENAMETOOLONG: name too long
```

**Solution:**
Windows has a 260-character path limit by default.

**Fix (Windows 10/11):**
1. Open PowerShell as Administrator:
   - Press `Windows Key`
   - Type "PowerShell"
   - Right-click "Windows PowerShell"
   - Select "Run as administrator"

2. Run this command:
   ```powershell
   New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
   ```

3. Restart your computer

**Alternative Solution:**
Move the project to a shorter path like:
```
C:\Projects\TheGrantScout\
```

### Issue 4: Port 3000 Already in Use

**Error Message:**
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solution 1 - Use a Different Port:**
```cmd
npm run dev -- -p 3001
```
Then open: `http://localhost:3001`

**Solution 2 - Kill the Process:**
1. Open Command Prompt as Administrator
2. Find what's using port 3000:
   ```cmd
   netstat -ano | findstr :3000
   ```
3. Note the PID number (last column)
4. Kill the process (replace 1234 with your PID):
   ```cmd
   taskkill /PID 1234 /F
   ```

### Issue 5: npm install Fails

**Error Message:**
```
npm ERR! code EINTEGRITY
```

**Solution:**
1. Delete the `node_modules` folder:
   - Go to the project folder in File Explorer
   - Delete the `node_modules` folder
   - Delete `package-lock.json` file

2. Clear npm cache:
   ```cmd
   npm cache clean --force
   ```

3. Try again:
   ```cmd
   npm install
   ```

### Issue 6: Firewall Blocking

**Issue:**
Firewall popup when running `npm run dev`

**Solution:**
1. Click "Allow access" when Windows Firewall asks
2. Both "Private networks" and "Public networks" can be checked
3. This is safe - it's just allowing your local development server

---

## Troubleshooting

### Development Server Won't Start

**Checklist:**
1. Are you in the correct folder? (`dir` should show package.json)
2. Did you run `npm install` first?
3. Is port 3000 available? (see Issue 4 above)
4. Any errors in the console? Read them carefully

### Website Shows Blank Page

**Checklist:**
1. Check the Command Prompt for errors
2. Open browser Developer Tools (press F12)
3. Look at the Console tab for JavaScript errors
4. Hard refresh the page: `Ctrl + Shift + R`

### Changes Not Showing

**Solutions:**
1. Hard refresh: `Ctrl + Shift + R`
2. Clear browser cache:
   - Chrome: `Ctrl + Shift + Delete`
   - Select "Cached images and files"
   - Click "Clear data"
3. Stop and restart the dev server:
   - Press `Ctrl + C` in Command Prompt
   - Run `npm run dev` again

### Need to Start Over?

If everything is broken and you want to start fresh:

1. Stop the development server (`Ctrl + C`)
2. Delete these folders/files:
   - `node_modules` (folder)
   - `.next` (folder)
   - `package-lock.json` (file)
3. Reinstall:
   ```cmd
   npm install
   ```
4. Start the server:
   ```cmd
   npm run dev
   ```

---

## Next Steps

### You're All Set! Now What?

1. **Read the Documentation:**
   - `PROJECT_PLAN.md` - Complete project overview
   - `docs/QUICK_START_GUIDE.md` - Quick reference for builders
   - `docs/BRANDING_GUIDE.md` - Brand colors and styles

2. **Start Building:**
   - Review the task list in `PROJECT_PLAN.md`
   - Begin with Task 1: Project Setup & Template Cloning
   - Follow the task sequence in order

3. **Use These Commands:**
   - `npm run dev` - Start development server
   - `npm run build` - Build for production
   - `npm start` - Run production build locally
   - `npm run lint` - Check code for errors

4. **Testing Your Work:**
   - See `docs/TESTING_CHECKLIST.md` for what to test
   - Test on mobile sizes regularly
   - Check browser console for errors

5. **Ready to Deploy:**
   - See `docs/DEPLOYMENT_GUIDE.md` when ready to go live

---

## Getting Help

### Resources

- **Next.js Documentation**: https://nextjs.org/docs
- **Tailwind CSS Docs**: https://tailwindcss.com/docs
- **npm Documentation**: https://docs.npmjs.com

### Common Commands Reference

See `docs/QUICK_COMMANDS.md` for a quick reference card.

### Still Stuck?

1. Google the exact error message (include "Next.js" or "npm" in your search)
2. Check Stack Overflow
3. Ask in the project mailbox (tag Project Manager)

---

## Tips for Windows Users

### Use PowerShell Instead (Optional)

PowerShell is more powerful than Command Prompt:
1. Press `Windows Key + X`
2. Select "Windows PowerShell"
3. All the same commands work!

### Windows Terminal (Windows 11 or Windows 10 with update)

Windows Terminal is even better:
1. Press `Windows Key`
2. Type "Terminal"
3. Open Windows Terminal
4. You can have multiple tabs, custom colors, etc.

### Path Shortcuts

Instead of typing long paths:
1. Navigate to folder in File Explorer
2. Click in the address bar
3. Type `cmd` or `powershell` and press Enter

### Tab Completion

In Command Prompt or PowerShell:
- Type the first few letters of a folder name
- Press `Tab` to auto-complete
- Press `Tab` again to cycle through options

Example:
```cmd
cd Bus<Tab>  → cd "Business Factory (Research) 11-1-2025"
```

---

## Summary

Congratulations! You now have:

- Node.js installed and working
- Code editor set up (VS Code)
- Project dependencies installed
- Development server running
- Website viewable in browser

**You're ready to build TheGrantScout!**

Next: Open `docs/TESTING_CHECKLIST.md` and `docs/QUICK_COMMANDS.md` for daily reference.

---

**Questions?** Tag the Project Manager in the team mailbox.

**Ready to deploy?** See `docs/DEPLOYMENT_GUIDE.md` when your website is complete.
