# Quick Start Guide - After Duplicate Fix

## What Changed?

✅ **Duplicates are now PREVENTED** through:
1. File sync fixes (no more caching issues)
2. User approval required before sending
3. Automatic duplicate detection
4. Dry-run mode for testing

## How to Use the Scripts Now

### Option 1: Test First (Recommended)

```bash
# Navigate to project directory
cd "/mnt/c/Business Factory (Research) 11-1-2025/06_GO_TO_MARKET/outreach_sequences/Email Campaign 2025-11-3"

# Run in dry-run mode (shows preview, doesn't send)
python send_initial_outreach.py --dry-run

# Review the output carefully
# - Check total emails
# - Verify sample addresses
# - Confirm no duplicates detected
```

### Option 2: Send for Real

```bash
# Run normally
python send_initial_outreach.py

# Script will show statistics and ask for approval:
#
# ╔══════════════════════════════════════════════════════════════════╗
# ║  SEND PREVIEW & APPROVAL                                         ║
# ╠══════════════════════════════════════════════════════════════════╣
# ║  EMAILS TO BE SENT TODAY:                                        ║
# ║  Grant Alerts            50 emails                               ║
# ║  TOTAL TO SEND: 50                                               ║
# ║  ✅ DUPLICATE CHECK: PASSED (no duplicates detected)            ║
# ╚══════════════════════════════════════════════════════════════════╝
#
# Type 'yes' or 'approve' to proceed, or 'no' to cancel:
# >

# Type 'yes' and press Enter to proceed
# Type 'no' to cancel

# Script will then send emails with proper delays
```

### Option 3: Follow-Up Emails

```bash
# Same workflow for follow-ups
python send_followup.py --dry-run   # Test first
python send_followup.py             # Send for real (requires approval)
```

## What to Look For

### Good Signs ✅
- "DUPLICATE CHECK: PASSED" message
- Numbers look reasonable
- Sample email addresses look correct
- Script asks for approval

### Warning Signs ⚠️
- "DUPLICATES DETECTED" warning
- Numbers seem too high or too low
- Sample addresses look wrong
- Script doesn't ask for approval (means you're using old version!)

### If You See Duplicates
**STOP** and cancel. Then:
1. Check if you're using the updated scripts
2. Review sent_tracker.csv manually
3. Contact support if issue persists

## Safety Features

### 1. Approval Required
- **You must type 'yes' to send**
- Can cancel anytime by typing 'no'
- Review stats carefully before approving

### 2. Duplicate Detection
- Automatic before every send
- Blocks sending if duplicates found
- Shows which emails are duplicates

### 3. Dry-Run Mode
- Safe testing without sending
- `--dry-run` flag
- Shows everything except actual sends

### 4. File Sync
- Writes are immediately saved to disk
- No more cache issues
- Works on WSL/Windows

## Common Commands

```bash
# Test initial outreach
python send_initial_outreach.py --dry-run

# Send initial outreach (requires approval)
python send_initial_outreach.py

# Test follow-ups
python send_followup.py --dry-run

# Send follow-ups (requires approval)
python send_followup.py

# Get help
python send_initial_outreach.py --help
python send_followup.py --help

# Check for duplicates in sent tracker
cd "/mnt/c/Business Factory (Research) 11-1-2025/06_GO_TO_MARKET/outreach_sequences"
awk -F',' 'NR>1 {print $2}' sent_tracker.csv | sort | uniq -d
# (should return nothing if no duplicates)
```

## Best Practices

1. **Always test with --dry-run first**
   - Especially after configuration changes
   - Before large sends
   - When unsure about anything

2. **Read approval prompt carefully**
   - Don't rush through it
   - Verify numbers make sense
   - Check that duplicate check passed

3. **Monitor sent_tracker.csv**
   - Check periodically for duplicates
   - Verify sends are being logged
   - Review if anything looks unusual

4. **Don't restart scripts rapidly**
   - Let them complete gracefully
   - Use Ctrl+C to interrupt (safe shutdown)
   - Wait a few seconds before restarting

5. **One script at a time**
   - Don't run multiple instances simultaneously
   - Coordinate with team if multiple people send

## Troubleshooting

### "No emails to send"
- This is normal if everyone has been contacted
- Check with --dry-run to see statistics

### "Duplicates detected in batch"
- Script is protecting you!
- Don't send - investigate first
- Check sent_tracker.csv manually

### Script doesn't ask for approval
- You're using the OLD version
- Re-download the updated scripts
- Check that you're in the right directory

### Emails still being sent after typing 'no'
- This shouldn't happen with the new version
- Use Ctrl+C to force stop if needed
- Report this issue immediately

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python send_initial_outreach.py --dry-run` | Test without sending |
| `python send_initial_outreach.py` | Send (requires approval) |
| `python send_followup.py --dry-run` | Test follow-ups |
| `python send_followup.py` | Send follow-ups (requires approval) |
| `--help` | Show help message |

## Need Help?

- **Full documentation**: See `DUPLICATE_FIX_REPORT.md`
- **Original guide**: See `USER_GUIDE.md`
- **Configuration**: See `config.py`

---

**Updated**: November 11, 2025
**Version**: 2.0 (with duplicate prevention)
**Status**: ✅ Safe to use
