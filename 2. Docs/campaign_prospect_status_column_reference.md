# campaign_prospect_status Column Reference

**Schema:** f990_2025
**Table:** campaign_prospect_status
**Rows:** 3,185
**Description:** Email campaign tracking table recording outreach status for each prospect, including send history, replies, bounces, and errors.

---

## Columns

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| id | integer | NO | Auto-incrementing primary key |
| ein | character varying(20) | YES | Organization EIN of the prospect |
| email | character varying(255) | YES | Email address used for outreach |
| org_name | text | YES | Organization name |
| org_type | character varying(20) | YES | Organization type: 'foundation' or 'nonprofit' |
| vertical | character varying(30) | NO | Campaign vertical/segment (e.g. state-sector cohort identifier) |
| campaign_status | character varying(30) | YES | Current status in the campaign lifecycle. Default: 'not_contacted'. Values: not_contacted, initial_sent, followup_sent, replied, bounced, unsubscribed. |
| initial_sent_at | timestamp without time zone | YES | Timestamp when the initial outreach email was sent |
| initial_status | character varying(20) | YES | Delivery status of the initial email (e.g. 'delivered', 'failed') |
| initial_subject | text | YES | Subject line of the initial outreach email |
| initial_sender | character varying(255) | YES | Sender email address or name for the initial email |
| followup_sent_at | timestamp without time zone | YES | Timestamp when the follow-up email was sent |
| followup_status | character varying(20) | YES | Delivery status of the follow-up email |
| followup_sender | character varying(255) | YES | Sender for the follow-up email |
| replied | boolean | YES | Whether the prospect replied to any outreach. Default: false. |
| replied_at | timestamp without time zone | YES | Timestamp of the reply |
| reply_notes | text | YES | Notes or summary of the reply content |
| bounced | boolean | YES | Whether the email bounced. Default: false. |
| bounced_at | timestamp without time zone | YES | Timestamp of the bounce |
| bounce_reason | text | YES | Reason for the bounce (e.g. 'invalid_email', 'mailbox_full') |
| send_error | boolean | YES | Whether there was an error sending. Default: false. |
| error_message | text | YES | Error message details |
| error_at | timestamp without time zone | YES | Timestamp of the error |
| unsubscribed | boolean | YES | Whether the prospect unsubscribed. Default: false. |
| unsubscribed_at | timestamp without time zone | YES | Timestamp of unsubscribe |
| source_file | character varying(100) | YES | CSV or batch file this record was imported from |
| created_at | timestamp without time zone | YES | When this row was first inserted. Default: now(). |
| updated_at | timestamp without time zone | YES | When this row was last modified. Default: now(). |
| notes | text | YES | Free-text notes about this prospect's outreach history |

---

## Primary Key
- `id` -- Auto-incrementing integer

## Foreign Keys
- No formal foreign keys. `ein` can be joined to `dim_foundations.ein`, `dim_recipients.ein`, `foundation_prospects2.ein`, or `nonprofits_prospects2.ein` depending on `org_type`.

## Indexes
- See database for current indexes

## Notes
- The `campaign_status` field tracks the overall lifecycle state. It progresses: not_contacted -> initial_sent -> followup_sent. It can also move to replied, bounced, or unsubscribed at any stage.
- The `vertical` column is NOT NULL and identifies which campaign cohort this prospect belongs to. Used for grouping and reporting.
- Boolean flags (`replied`, `bounced`, `send_error`, `unsubscribed`) default to false and are set to true when the corresponding event occurs.
- The `email` field may contain addresses that later bounced. Check `bounced = true` before re-sending.
- Related views: `v_campaign_prospects` (enriched view), `v_suppress_list` (emails to suppress), `v_suppress_list_by_ein` (orgs to suppress).
- The `source_file` column tracks which batch import created the record, useful for auditing campaign waves.
