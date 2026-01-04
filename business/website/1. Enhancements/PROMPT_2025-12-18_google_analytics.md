# PROMPT: Add Google Analytics Tag to Website

**Date:** 2025-12-18  
**For:** Claude Code CLI

---

## Task

Add the Google Analytics gtag.js script to TheGrantScout website.

## Google Tag Code

Add this immediately after the opening `<head>` tag on every page:

```html
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-QDCG0DXNXF"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-QDCG0DXNXF');
</script>
```

## Steps

1. Find all HTML files in the website directory
2. Add the Google tag code immediately after each `<head>` tag
3. If using a templating system (e.g., base template, layout file), add it once to the base template
4. Verify the tag appears on all pages

## Notes

- Place immediately after `<head>`, before any other scripts
- Don't add duplicate tags if already present
- Tag ID: `G-QDCG0DXNXF`
