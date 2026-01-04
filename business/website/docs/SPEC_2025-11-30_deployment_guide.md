# TheGrantScout Website - Deployment Guide

Complete guide for deploying TheGrantScout website to production at thegrantscout.com.

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Deployment Option 1: Vercel (Recommended)](#deployment-option-1-vercel-recommended)
4. [Deployment Option 2: Manual Static Export](#deployment-option-2-manual-static-export)
5. [Domain Configuration](#domain-configuration)
6. [Post-Deployment Verification](#post-deployment-verification)
7. [Troubleshooting](#troubleshooting)
8. [Updating the Site](#updating-the-site)

---

## Deployment Overview

### What You're Deploying

- **Project**: TheGrantScout landing page
- **Framework**: Next.js 14+
- **Domain**: thegrantscout.com (already owned)
- **Target URL**: https://thegrantscout.com

### Recommended Platform: Vercel

**Why Vercel?**
- Created by Next.js team (perfect integration)
- Free tier available
- Automatic HTTPS (SSL certificate)
- Global CDN (fast worldwide)
- Easy custom domain setup
- Automatic deployments from Git
- Zero configuration needed

**Alternatives:**
- Netlify (similar to Vercel)
- AWS Amplify (more complex)
- Static export to any web host (requires more setup)

### Timeline

- **First-time deployment**: 30-60 minutes
- **Updates after initial setup**: 5 minutes

---

## Pre-Deployment Checklist

Before deploying, ensure everything is ready:

### Content Review

- [ ] All placeholder text replaced with final copy
- [ ] All placeholder images replaced (or removed)
- [ ] Spelling and grammar checked
- [ ] Contact email addresses correct:
  - [ ] hello@thegrantscout.com
  - [ ] support@thegrantscout.com
- [ ] Pricing is accurate
- [ ] Launch offers/deadlines are current
- [ ] Copyright year is correct: © 2025
- [ ] Privacy Policy ready (even if basic)
- [ ] Terms of Service ready (even if basic)

### Technical Review

- [ ] Production build works locally:
  ```cmd
  npm run build
  npm start
  ```
- [ ] No console errors when testing
- [ ] All links work (no 404s)
- [ ] All images load correctly
- [ ] Forms submit correctly (if applicable)
- [ ] Mobile responsive at all sizes
- [ ] Tested on Chrome, Edge, and Firefox

### Performance Review

- [ ] Lighthouse Performance score: 90+
- [ ] Lighthouse Accessibility score: 90+
- [ ] Lighthouse SEO score: 90+
- [ ] All images optimized
- [ ] Page loads in < 3 seconds

### SEO Review

- [ ] Title tag is compelling
- [ ] Meta description is compelling
- [ ] Open Graph image exists (1200x630px)
- [ ] Favicon files exist
- [ ] robots.txt allows indexing
- [ ] Sitemap exists or will be auto-generated

### Environment Variables

Check if you have any API keys or secrets:
- [ ] Google Analytics ID (if ready)
- [ ] Form submission endpoint (if applicable)
- [ ] Any other API keys

**Important**: These will need to be added to Vercel separately!

---

## Deployment Option 1: Vercel (Recommended)

This is the recommended method for deploying TheGrantScout website.

### Step 1: Create a Vercel Account

1. Go to https://vercel.com
2. Click "Sign Up" (top right)
3. Choose sign-up method:
   - **Recommended**: "Continue with GitHub" (easiest)
   - Alternative: "Continue with Email"
4. Complete the sign-up process
5. Verify your email (if using email sign-up)

**Cost**: Free for personal projects

### Step 2: Prepare Your Code

**Option A: Using GitHub (Recommended)**

1. Create a GitHub account (if you don't have one):
   - Go to https://github.com
   - Click "Sign up"
   - Follow the process

2. Create a new repository:
   - Go to https://github.com/new
   - Repository name: `thegrantscout-landing`
   - Description: "TheGrantScout landing page"
   - Select "Private" (or Public if you want)
   - Do NOT initialize with README (we already have code)
   - Click "Create repository"

3. Push your code to GitHub:

   Open Command Prompt in your project folder:
   ```cmd
   cd "C:\Business Factory (Research) 11-1-2025\01_VALIDATED_IDEAS\TIER_1_BOOTSTRAPPED\IDEA_062_Grant_Alerts\TheGrantScout\3. Website\thegrantscout-landing"
   ```

   Run these commands:
   ```cmd
   git init
   git add .
   git commit -m "Initial commit - TheGrantScout landing page"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/thegrantscout-landing.git
   git push -u origin main
   ```

   Replace `YOUR-USERNAME` with your actual GitHub username.

**Option B: Direct Upload to Vercel**

If you don't want to use GitHub:
- You can drag-and-drop your project folder in Vercel
- Less convenient for updates, but works fine

### Step 3: Import Project to Vercel

1. Log into Vercel: https://vercel.com
2. Click "Add New..." → "Project"
3. Choose your method:

**If Using GitHub:**
1. Click "Import Git Repository"
2. Find `thegrantscout-landing` in the list
3. Click "Import"

**If Using Direct Upload:**
1. Click "Browse" or drag project folder
2. Upload the entire `thegrantscout-landing` folder

### Step 4: Configure Project Settings

Vercel will auto-detect Next.js. Verify these settings:

**Project Name:**
- Name: `thegrantscout-landing` (or `thegrantscout`)

**Framework Preset:**
- Should say "Next.js" (auto-detected)

**Build and Output Settings:**
- Build Command: `npm run build` (or leave blank - uses default)
- Output Directory: `.next` (or leave blank)
- Install Command: `npm install` (or leave blank)

**Root Directory:**
- Leave as `./` (unless project is in a subfolder)

### Step 5: Add Environment Variables (If Needed)

If you have API keys or environment variables:

1. Expand "Environment Variables" section
2. Add each variable:
   - Key: `NEXT_PUBLIC_GA_ID` (example)
   - Value: `G-XXXXXXXXXX` (your actual ID)
   - Click "Add"

**Common Variables:**
- `NEXT_PUBLIC_GA_ID` - Google Analytics ID
- `NEXT_PUBLIC_FORM_ENDPOINT` - Form submission URL
- Add others as needed

**Important**:
- Variables starting with `NEXT_PUBLIC_` are visible in browser
- Don't put secrets in `NEXT_PUBLIC_` variables
- Sensitive keys should NOT have `NEXT_PUBLIC_` prefix

### Step 6: Deploy

1. Click "Deploy" button
2. Wait for deployment (usually 2-3 minutes)
3. Watch the build logs
4. When you see "Ready" and confetti animation, you're live!

**Your Preview URL:**
Vercel gives you a URL like:
- `https://thegrantscout-landing.vercel.app`
- Or: `https://thegrantscout-landing-abc123.vercel.app`

### Step 7: Test Your Preview Site

1. Click the preview URL
2. Test the entire site:
   - [ ] All pages load
   - [ ] All images display
   - [ ] Navigation works
   - [ ] Forms work (if applicable)
   - [ ] No console errors (F12 → Console)
3. Test on mobile (real device or Chrome DevTools)

### Step 8: Connect Custom Domain

Now let's connect thegrantscout.com to your Vercel deployment.

**In Vercel Dashboard:**

1. Go to your project
2. Click "Settings" (top menu)
3. Click "Domains" (left sidebar)
4. In "Add Domain" field, type: `thegrantscout.com`
5. Click "Add"
6. Vercel will provide DNS configuration instructions

**You'll see something like:**
```
Add the following DNS records to your domain:

Type    Name    Value
A       @       76.76.21.21
CNAME   www     cname.vercel-dns.com
```

(Note: These are example IPs, Vercel will give you the actual ones)

### Step 9: Configure DNS Records

You need to update DNS where your domain is registered.

**Find Where Your Domain is Registered:**
- Check your email for domain purchase confirmation
- Common registrars: GoDaddy, Namecheap, Google Domains, Cloudflare

**Update DNS Records:**

**Example for GoDaddy:**
1. Log into GoDaddy
2. Go to "My Products"
3. Find thegrantscout.com
4. Click "DNS" or "Manage DNS"
5. Look for existing "A" and "CNAME" records
6. Delete or modify to match Vercel's instructions:

   **A Record:**
   - Type: A
   - Name: @ (or leave blank)
   - Value: [IP address from Vercel]
   - TTL: 1 hour (or default)

   **CNAME Record for www:**
   - Type: CNAME
   - Name: www
   - Value: cname.vercel-dns.com (or what Vercel provides)
   - TTL: 1 hour (or default)

7. Click "Save"

**Example for Namecheap:**
1. Log into Namecheap
2. Go to "Domain List"
3. Click "Manage" next to thegrantscout.com
4. Click "Advanced DNS"
5. Add/modify records to match Vercel's instructions
6. Click "Save"

**Example for Cloudflare:**
1. Log into Cloudflare
2. Select thegrantscout.com
3. Click "DNS"
4. Add/modify records to match Vercel's instructions
5. Make sure "Proxy status" is orange cloud (proxied) or gray (DNS only)
6. Click "Save"

### Step 10: Wait for DNS Propagation

DNS changes take time to spread across the internet.

**Typical wait times:**
- Minimum: 10-30 minutes
- Average: 1-4 hours
- Maximum: 24-48 hours (rare)

**Check if DNS has propagated:**
1. Go to https://dnschecker.org
2. Enter: thegrantscout.com
3. Select record type: A
4. Click "Search"
5. Look for Vercel's IP address to appear in multiple locations

### Step 11: Verify SSL Certificate

Once DNS is configured:

1. Vercel automatically issues SSL certificate (HTTPS)
2. This usually happens within 1-2 hours after DNS propagation
3. Check in Vercel → Settings → Domains
4. You should see a green checkmark next to thegrantscout.com

**If SSL is not issued:**
- Wait longer (up to 24 hours)
- Make sure DNS records are correct
- Contact Vercel support if needed

### Step 12: Configure www Redirect

Make sure www.thegrantscout.com redirects to thegrantscout.com (or vice versa).

**In Vercel:**
1. Add both domains:
   - thegrantscout.com
   - www.thegrantscout.com
2. Set one as primary (recommended: thegrantscout.com without www)
3. Vercel automatically redirects the other to the primary

---

## Deployment Option 2: Manual Static Export

If you want to host on a traditional web host (not Vercel).

### Step 1: Configure Next.js for Static Export

1. Open `next.config.js` in your project
2. Add this configuration:
   ```javascript
   /** @type {import('next').NextConfig} */
   const nextConfig = {
     output: 'export',
     images: {
       unoptimized: true, // Required for static export
     },
   }

   module.exports = nextConfig
   ```

### Step 2: Build for Production

In Command Prompt:

```cmd
cd "C:\Business Factory (Research) 11-1-2025\01_VALIDATED_IDEAS\TIER_1_BOOTSTRAPPED\IDEA_062_Grant_Alerts\TheGrantScout\3. Website\thegrantscout-landing"
npm run build
```

This creates an `out` folder with all static files.

### Step 3: Test the Export Locally

```cmd
npx serve out
```

Open http://localhost:3000 and test everything works.

### Step 4: Upload to Web Host

**Upload the `out` folder contents to your web host:**

**Via FTP (e.g., FileZilla):**
1. Download FileZilla: https://filezilla-project.org
2. Connect to your web host using FTP credentials
3. Navigate to public_html or www folder
4. Upload ALL files from the `out` folder
5. Keep folder structure intact

**Via Web Host Control Panel (e.g., cPanel):**
1. Log into your hosting control panel
2. Go to "File Manager"
3. Navigate to public_html or www folder
4. Upload ALL files from the `out` folder
5. Extract if uploaded as ZIP

### Step 5: Configure Web Server

**For Apache (.htaccess file):**

Create a `.htaccess` file in your web root with:

```apache
# Force HTTPS
RewriteEngine On
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Redirect www to non-www (or vice versa)
RewriteCond %{HTTP_HOST} ^www\.thegrantscout\.com [NC]
RewriteRule ^(.*)$ https://thegrantscout.com/$1 [L,R=301]

# Enable compression
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript
</IfModule>

# Enable caching
<IfModule mod_expires.c>
  ExpiresActive On
  ExpiresByType image/jpg "access plus 1 year"
  ExpiresByType image/jpeg "access plus 1 year"
  ExpiresByType image/gif "access plus 1 year"
  ExpiresByType image/png "access plus 1 year"
  ExpiresByType text/css "access plus 1 month"
  ExpiresByType application/javascript "access plus 1 month"
</IfModule>
```

**For Nginx:**

Add to your server block:

```nginx
server {
    listen 80;
    server_name thegrantscout.com www.thegrantscout.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name www.thegrantscout.com;
    return 301 https://thegrantscout.com$request_uri;
}

server {
    listen 443 ssl http2;
    server_name thegrantscout.com;

    root /var/www/thegrantscout;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

---

## Domain Configuration

### DNS Records Summary

**Required DNS Records:**

| Type  | Name | Value                    | Purpose                |
|-------|------|--------------------------|------------------------|
| A     | @    | [Your server IP]         | Points root domain     |
| CNAME | www  | thegrantscout.com        | Points www subdomain   |

**Optional Records:**

| Type  | Name | Value                    | Purpose                |
|-------|------|--------------------------|------------------------|
| MX    | @    | [Your email server]      | For email receiving    |
| TXT   | @    | [SPF/DKIM]               | For email security     |

### Email Configuration

To use hello@thegrantscout.com and support@thegrantscout.com:

**Option 1: Google Workspace (Paid)**
- Cost: ~$6/user/month
- Professional email hosting
- Gmail interface
- Configure MX records provided by Google

**Option 2: Zoho Mail (Free/Paid)**
- Free tier: 5GB storage
- Configure MX records provided by Zoho
- Basic email functionality

**Option 3: Email Forwarding (Easiest)**
- Forward to existing email (Gmail, Outlook, etc.)
- Set up in domain registrar
- No cost

**Configure Email Forwarding (Example):**
1. Log into domain registrar
2. Find "Email Forwarding" settings
3. Add forwards:
   - hello@thegrantscout.com → your-email@gmail.com
   - support@thegrantscout.com → your-email@gmail.com
4. Save

---

## Post-Deployment Verification

### Immediate Checks (First Hour)

**Website Access:**
- [ ] https://thegrantscout.com loads
- [ ] https://www.thegrantscout.com redirects to non-www (or vice versa)
- [ ] SSL certificate is active (padlock icon in browser)
- [ ] No browser warnings about security

**Content Check:**
- [ ] All pages load correctly
- [ ] All images display
- [ ] Navigation works
- [ ] All links work (no 404s)
- [ ] Forms submit (if applicable)

**Mobile Check:**
- [ ] Site loads on mobile browser
- [ ] Layout is responsive
- [ ] All interactions work

**Performance Check:**
1. Open https://pagespeed.web.dev
2. Enter: https://thegrantscout.com
3. Click "Analyze"
4. Check scores:
   - [ ] Performance: 90+
   - [ ] Accessibility: 90+
   - [ ] SEO: 90+

**Console Check:**
- [ ] No JavaScript errors (F12 → Console)
- [ ] No 404 errors in Network tab

### First Day Checks

**Search Engines:**
1. Submit to Google Search Console:
   - Go to https://search.google.com/search-console
   - Add property: thegrantscout.com
   - Verify ownership (Vercel has automatic verification)
   - Submit sitemap: https://thegrantscout.com/sitemap.xml

2. Check indexing:
   - Google: Search `site:thegrantscout.com`
   - Should show your site (may take 1-7 days)

**Analytics (if configured):**
- [ ] Google Analytics tracking (visit site, check Real-Time)
- [ ] Event tracking works (click a CTA, check Events in GA)

**Email:**
- [ ] Send test email to hello@thegrantscout.com
- [ ] Verify it arrives at forwarding destination
- [ ] Send test email to support@thegrantscout.com
- [ ] Verify it arrives

**Backup:**
- [ ] Download a backup of deployed code
- [ ] Save Vercel project settings/environment variables
- [ ] Document deployment process (you're reading it!)

### First Week Monitoring

**Daily Checks:**
- [ ] Site is accessible
- [ ] Forms are submitting (if applicable)
- [ ] No error reports

**Analytics Review:**
- [ ] Check traffic sources
- [ ] Check bounce rate (target: < 60%)
- [ ] Check average time on page (target: > 2 minutes)
- [ ] Check CTA click rate

**Performance Monitoring:**
- [ ] Run Lighthouse audit
- [ ] Check load times
- [ ] Monitor error logs (Vercel dashboard)

---

## Troubleshooting

### Site Not Loading

**Check DNS:**
1. Go to https://dnschecker.org
2. Enter thegrantscout.com
3. Verify A record points to correct IP

**Check Vercel Deployment:**
1. Log into Vercel
2. Check deployment status
3. Look for errors in build logs

**Clear Browser Cache:**
1. Hard refresh: `Ctrl + Shift + R`
2. Or clear cache: `Ctrl + Shift + Delete`

### SSL Certificate Not Working

**Symptoms:**
- "Not Secure" in browser
- Certificate warning

**Solutions:**
1. Wait 1-2 hours after DNS propagation
2. Verify DNS records are correct
3. In Vercel, remove and re-add domain
4. Contact Vercel support

### www Not Redirecting

**Check Vercel:**
1. Settings → Domains
2. Verify both thegrantscout.com and www.thegrantscout.com are added
3. Verify one is set as "Primary"

**Check DNS:**
1. Verify CNAME record for www is correct
2. Wait for DNS propagation

### Images Not Loading

**Check Image Paths:**
- Use `/images/filename.jpg` (absolute path)
- Not `./images/filename.jpg` (relative path)

**Check Next.js Image Component:**
- If using static export, images need `unoptimized: true`

### Forms Not Submitting

**Check Endpoint:**
- Verify form submission URL is correct
- Check CORS settings on backend
- Check browser console for errors

**Check Environment Variables:**
- Verify API keys are added in Vercel
- Verify variable names are correct (case-sensitive)

---

## Updating the Site

### Making Changes

**If Using Vercel + GitHub (Recommended):**

1. Make changes locally
2. Test locally: `npm run dev`
3. Commit changes:
   ```cmd
   git add .
   git commit -m "Update hero section copy"
   git push
   ```
4. Vercel automatically deploys changes (2-3 minutes)
5. Check preview URL
6. Changes are live!

**If Using Manual Static Export:**

1. Make changes locally
2. Test locally: `npm run dev`
3. Build new export: `npm run build`
4. Upload new `out` folder to web host
5. Clear cache (may take a few hours to show)

### Rolling Back Changes

**In Vercel:**
1. Go to project
2. Click "Deployments"
3. Find previous working deployment
4. Click "..." menu → "Promote to Production"

**In Manual Hosting:**
1. Upload previous version of files
2. Or restore from backup

### Testing Before Deploy

**Create a Staging Environment:**
1. In Vercel, deploy to a different domain first
2. Test thoroughly
3. Then deploy to production

---

## Post-Launch Checklist

After successful deployment:

### Week 1

- [ ] Monitor uptime (use UptimeRobot.com - free)
- [ ] Check analytics daily
- [ ] Test forms regularly
- [ ] Monitor Google Search Console for errors
- [ ] Respond to any user-reported issues

### Week 2-4

- [ ] Review analytics for patterns
- [ ] Identify pages with high bounce rate
- [ ] A/B test headlines/CTAs (if desired)
- [ ] Gather user feedback
- [ ] Plan iterations based on data

### Monthly

- [ ] Run Lighthouse audit
- [ ] Check for broken links
- [ ] Update content as needed
- [ ] Review and update pricing (if changed)
- [ ] Renew domain (if expiring)

---

## Additional Resources

### Vercel Documentation
- Getting Started: https://vercel.com/docs
- Custom Domains: https://vercel.com/docs/concepts/projects/domains
- Environment Variables: https://vercel.com/docs/concepts/projects/environment-variables

### Next.js Documentation
- Static Export: https://nextjs.org/docs/app/building-your-application/deploying/static-exports
- Deployment: https://nextjs.org/docs/deployment

### DNS Resources
- DNS Checker: https://dnschecker.org
- What is DNS: https://www.cloudflare.com/learning/dns/what-is-dns/

### Performance Tools
- PageSpeed Insights: https://pagespeed.web.dev
- GTmetrix: https://gtmetrix.com
- WebPageTest: https://www.webpagetest.org

### Monitoring Tools
- UptimeRobot (free uptime monitoring): https://uptimerobot.com
- Google Search Console: https://search.google.com/search-console

---

## Summary

**Recommended Deployment Path:**
1. Create Vercel account (free)
2. Push code to GitHub
3. Import project to Vercel
4. Deploy to preview URL
5. Test thoroughly
6. Connect custom domain (thegrantscout.com)
7. Configure DNS records
8. Wait for DNS propagation (1-4 hours)
9. Verify SSL certificate
10. Test live site
11. Submit to Google Search Console
12. Monitor and maintain

**Time Required:**
- Initial setup: 30-60 minutes
- DNS propagation wait: 1-4 hours
- Future updates: 5 minutes (automatic)

**Costs:**
- Vercel: Free (for this project size)
- Domain: Already owned
- SSL Certificate: Free (via Vercel)
- Email: Free (via forwarding) or $6/month (Google Workspace)

**You're live at https://thegrantscout.com!**

---

**Questions?** Tag the Project Manager in the team mailbox.

**Need help?** Vercel support is responsive and helpful for deployment issues.
