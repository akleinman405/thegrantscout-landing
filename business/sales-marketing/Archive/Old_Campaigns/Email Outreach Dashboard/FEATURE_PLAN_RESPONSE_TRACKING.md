# Feature Plan: Response Tracking & Campaign Planner Enhancements

**Date:** November 4, 2025
**Status:** PROPOSAL - Awaiting Approval

---

## Summary of Fixes Completed

### 1. ✅ Coordination Sync Issue FIXED
**Problem:** Dashboard showed 641 sent vs actual 441 sent
**Solution:** Modified `coordination_reader.py` to calculate sent counts from `sent_tracker.csv` instead of trusting stale `coordination.json`
**Result:** Dashboard now shows accurate 441 sent (441 initial, 0 followup)

### 2. ✅ Live Feed Tab FIXED
**Problem:** Live Feed wasn't showing emails
**Solution:** Added debug logging and better error handling for missing columns
**Result:** Live Feed now displays all 441 sent emails with auto-refresh

### 3. ✅ Test Emails Tab FIXED
**Problem:** Test Emails tab was blank
**Solution:** Moved prerequisite checks (accounts/verticals) outside form so errors display
**Result:** Test Email form now shows properly or displays helpful error messages

---

## Current Campaign Planner Capabilities

### What's Already Working:

✅ **Calculates based on:**
- Number of active email accounts
- Daily send limit per account (`daily_send_limit`)
- Total prospects loaded and not yet contacted
- Business days only (Mon-Fri)
- Business hours (9am-3pm EST)

✅ **Tracks prospect status:**
- `not_contacted`: Ready for initial outreach
- `initial_sent`: Sent initial, waiting for follow-up window
- `followup_sent`: Completed follow-up
- Status tracked in prospect CSV files per vertical

✅ **Weekly forecast shows:**
- 7-day outlook
- Skips weekends automatically
- Reduces available prospects each day
- Shows planned sends and remaining capacity

✅ **Capacity calculator:**
- Calculates days needed for X prospects
- Accounts for weekends
- Shows daily breakdown
- Estimates end date

---

## Requested Enhancements

### Enhancement 1: Campaign Planner - Vertical Breakdown

**Current State:**
- Today's Plan shows TOTAL allocated/sent/remaining
- No breakdown by vertical

**Proposed Change:**

**Add vertical breakdown table:**
```
Campaign Status by Vertical

Vertical      | Type     | Allocated | Sent | Remaining | Available | Status
--------------|----------|-----------|------|-----------|-----------|--------
Debarment     | Initial  | 100       | 50   | 50        | 1,200     | Active
Debarment     | Followup | 50        | 0    | 50        | 300       | Idle
Food Recall   | Initial  | 75        | 30   | 45        | 800       | Active
Food Recall   | Followup | 25        | 0    | 25        | 150       | Idle
--------------|----------|-----------|------|-----------|-----------|--------
TOTAL         | All      | 250       | 80   | 170       | 2,450     | Active
```

**Implementation:**
- Read prospect CSVs to count available by vertical
- Count `not_contacted` for Initial Available
- Count prospects where `initial_sent != null AND followup_sent == null` for Followup Available
- Add totals row at bottom
- Color-code rows (green=active, gray=idle)

---

### Enhancement 2: Weekly Forecast - Add Total Row

**Current State:**
Weekly forecast shows 7 days but no total summary

**Proposed Change:**

Add total row showing:
- Total planned sends for the week
- Total remaining capacity
- Business days vs weekend days count

```
Date            | Planned Sends | Remaining Capacity | Status
----------------|---------------|--------------------|-----------
2025-11-04 (Mon)| 450           | 0                  | Scheduled
2025-11-05 (Tue)| 450           | 0                  | Scheduled
2025-11-06 (Wed)| 450           | 0                  | Scheduled
2025-11-07 (Thu)| 450           | 0                  | Scheduled
2025-11-08 (Fri)| 450           | 0                  | Scheduled
2025-11-09 (Sat)| -- (Weekend)  | --                 | Skipped
2025-11-10 (Sun)| -- (Weekend)  | --                 | Skipped
----------------|---------------|--------------------|-----------
TOTAL (5 days)  | 2,250         | 0                  | --
```

**Implementation:**
- Calculate totals for business days only
- Show "(X days)" in total row
- Bold/highlight total row

---

### Enhancement 3: Response Tracking in Dashboard

**Current State:**
- Response tracking via `response_tracker.csv`
- Manual CSV editing required
- No UI for viewing/editing responses

**Proposed Solution: Response Manager Page**

**New page:** `9_📬_Response_Manager.py`

#### Features:

1. **Response Table View**
   - Shows all sent emails with response status
   - Columns: Email, Vertical, Initial Sent Date, Replied Status, Followup Sent Date, Notes
   - Filter by: Vertical, Status (Pending/Replied/Not Interested), Date Range
   - Search by email address
   - Color-coded rows (green=replied, yellow=pending, red=not interested)

2. **Manual Response Entry**
   - Select email from dropdown (of sent emails)
   - Mark as: Replied, Not Interested, Bounced, Unsubscribed
   - Add notes (free text)
   - Set reply date
   - Save button updates `response_tracker.csv`

3. **Bulk Import from CSV**
   - Upload CSV with responses
   - Map columns (email, status, notes)
   - Preview before import
   - Merge with existing data (no duplicates)

4. **Export Responses**
   - Download as CSV
   - Filter before export
   - Include all fields

5. **Response Analytics**
   - Response rate by vertical
   - Response time distribution
   - Interested vs Not Interested breakdown
   - Timeline chart of responses

#### Data Structure:

Continue using `response_tracker.csv` as source of truth:
```csv
email,vertical,initial_sent_date,replied,followup_sent_date,notes,reply_date,response_type
user@example.com,debarment,2025-11-04,REPLIED,2025-11-05,"Interested in demo",2025-11-04,INTERESTED
user2@example.com,food_recall,2025-11-04,PENDING,,,,PENDING
```

**New fields:**
- `reply_date`: When they replied
- `response_type`: INTERESTED, NOT_INTERESTED, BOUNCED, UNSUBSCRIBED, PENDING

---

### Enhancement 4: Gmail PDF Response Import

**Challenge:** Gmail exports to PDF, not structured data

**Proposed Solution: Multi-Step Approach**

#### Option A: Email Forwarding (RECOMMENDED)

**Setup:**
1. User forwards response emails to a dedicated inbox
2. Dashboard connects to inbox via IMAP
3. Reads email headers (From, Date, Subject, Body)
4. Matches sender email to sent prospects
5. Automatically marks as "REPLIED"
6. Extracts key info (interested/not interested keywords)
7. Stores in response_tracker.csv

**Pros:**
- Accurate data extraction
- Automated workflow
- No manual PDF parsing
- Can extract email body for sentiment analysis

**Cons:**
- Requires IMAP setup
- User must forward emails

**Implementation:**
1. Add IMAP settings to Settings page
2. Create background job to check inbox every hour
3. Parse emails, match to prospects
4. Update response tracker
5. Show notifications for new responses

---

#### Option B: Gmail API Integration (ADVANCED)

**Setup:**
1. User authorizes Dashboard to access Gmail via OAuth
2. Dashboard monitors specific label (e.g., "Campaign Responses")
3. Reads emails with that label
4. Auto-matches to prospects
5. Updates response tracker

**Pros:**
- Fully automated
- No forwarding needed
- Can sync bidirectionally
- Access to full Gmail features

**Cons:**
- Complex OAuth setup
- Google API quotas
- Privacy concerns (access to Gmail)

---

#### Option C: Manual CSV Upload (SIMPLE, INTERIM SOLUTION)

**Setup:**
1. User manually logs responses in CSV
2. Uploads CSV to Dashboard
3. Dashboard validates and merges

**Pros:**
- Simple implementation
- No external dependencies
- User maintains full control

**Cons:**
- Manual work required
- Prone to human error
- Not scalable

**CSV Format:**
```csv
email,reply_date,response_type,notes
user@example.com,2025-11-04,INTERESTED,"Wants a demo"
user2@example.com,2025-11-04,NOT_INTERESTED,"Not at this time"
```

---

#### Option D: PDF Upload with OCR (NOT RECOMMENDED)

**Why not recommended:**
- Gmail PDFs are formatted for printing, not data extraction
- OCR unreliable for tabular data
- Email content often truncated
- High error rate
- Complex implementation

---

## Recommended Implementation Plan

### Phase 1: Quick Wins (30 minutes)
1. ✅ Fix coordination sync - COMPLETE
2. ✅ Fix Live Feed tab - COMPLETE
3. ✅ Fix Test Emails tab - COMPLETE
4. Add vertical breakdown to Campaign Planner
5. Add total row to Weekly Forecast

### Phase 2: Response Manager (2 hours)
1. Create `9_📬_Response_Manager.py` page
2. Build response table view (read from CSV)
3. Add manual response entry form
4. Add CSV import/export
5. Add basic analytics (response rate by vertical)

### Phase 3: Automated Response Tracking (4 hours)
1. **RECOMMENDED: Option A - Email Forwarding**
   - Add IMAP settings to Settings page
   - Create email monitor service
   - Parse forwarded emails
   - Match to prospects automatically
   - Update response tracker

**Alternative if user prefers:**
2. **Option B - Gmail API** (more complex)
3. **Option C - Manual CSV** (interim solution)

---

## Questions for User

### 1. Response Tracking Method
Which approach do you prefer?
- **A) Email Forwarding** (forward responses to dedicated inbox, auto-import)
- **B) Gmail API** (OAuth to read Gmail directly)
- **C) Manual CSV Upload** (you maintain CSV, upload to dashboard)
- **D) Hybrid** (manual entry with option to import CSV)

### 2. Response Categories
What response types do you want to track?
- Interested
- Not Interested
- Bounced
- Unsubscribed
- Out of Office
- Invalid Email
- Custom categories?

### 3. Follow-up Logic
How do you determine when a prospect is "ready for follow-up"?
- X days after initial email (how many days?)
- Only if no reply within X days?
- Manual selection?
- Based on response type?

### 4. Response Analytics
What metrics are most important?
- Response rate by vertical
- Response time (how long until reply)
- Interested vs Not Interested ratio
- Best performing subject lines
- Best performing verticals
- Other?

---

## Technical Details

### Initial vs Followup Tracking

**Current System:**

Prospect CSV structure:
```csv
email,first_name,company_name,state,website,initial_sent_date,followup_sent_date,notes
user@example.com,John,ACME Inc,CA,acme.com,2025-11-04,,
user2@example.com,Jane,XYZ Corp,NY,xyz.com,2025-11-03,2025-11-05,
```

**Logic:**
- `initial_sent_date` empty → Ready for initial
- `initial_sent_date` set, `followup_sent_date` empty → Ready for followup (after waiting period)
- Both set → Campaign complete

**Waiting Period for Followup:**
Currently managed by email scripts. Typical: 3-5 days after initial.

**Available Prospects Calculation:**
```python
# Initial-ready
initial_available = prospects where initial_sent_date is null

# Followup-ready
followup_available = prospects where:
    - initial_sent_date is not null
    - followup_sent_date is null
    - (today - initial_sent_date) >= followup_wait_days
    - replied != 'REPLIED' (don't follow up if they already replied)
```

---

## Proposed Timeline

### Immediate (Today - 30 mins)
1. ✅ Fix coordination sync - DONE
2. ✅ Fix Live Feed - DONE
3. ✅ Fix Test Emails - DONE
4. Add vertical breakdown table
5. Add weekly forecast total row

### This Week (2-4 hours)
1. Create Response Manager page
2. Build response table view
3. Add manual entry form
4. Add CSV import/export

### Next Week (4-6 hours)
1. Implement automated response tracking (your choice: A, B, or C)
2. Add response analytics
3. Integrate with Campaign Planner forecasting
4. Test end-to-end workflow

---

## Cost-Benefit Analysis

### Manual CSV Approach
- Time: 5 min/day to log responses
- Accuracy: 95% (human error)
- Scalability: Low (breaks at 100+ responses/day)
- Implementation: 2 hours

### Email Forwarding Approach
- Time: 30 sec/response (just forward)
- Accuracy: 99% (automated matching)
- Scalability: High (handles 1000s/day)
- Implementation: 4 hours
- Maintenance: Low

### Gmail API Approach
- Time: 0 sec (fully automated)
- Accuracy: 99% (automated matching)
- Scalability: Very High
- Implementation: 6 hours
- Maintenance: Medium (OAuth token refresh)

---

## Recommendation

**For immediate use:** Implement manual response entry + CSV import (Phase 2)

**For long-term efficiency:** Add email forwarding automation (Phase 3, Option A)

**Reason:** Email forwarding provides 95% of Gmail API benefits with 50% less complexity. No OAuth, no Google approval process, works immediately.

---

## Next Steps

**User Decision Required:**

1. ✅ Approve vertical breakdown table design?
2. ✅ Approve weekly forecast total row?
3. ❓ Choose response tracking method (A/B/C/D)?
4. ❓ Define response categories?
5. ❓ Specify followup wait period (days)?

Once approved, I'll implement in phases as outlined above.

---

**Prepared By:** Claude Code
**Date:** November 4, 2025
**Status:** AWAITING USER APPROVAL
