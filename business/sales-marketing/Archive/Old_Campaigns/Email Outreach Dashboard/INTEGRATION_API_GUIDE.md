# Integration Layer API - Quick Reference Guide

**For Frontend Developer**

This guide shows you how to use the integration layer functions in your Streamlit pages.

---

## Setup

```python
# Add these imports to your Streamlit pages
from integrations import (
    read_prospects,
    append_prospects,
    get_daily_metrics,
    get_vertical_breakdown,
    get_allocation_status,
    read_sent_tracker,
    get_prospect_stats
)

from utils import (
    format_number,
    format_percentage,
    format_date,
    format_time_ago,
    format_quota,
    validate_prospect_csv
)
```

---

## Common Use Cases

### 1. Dashboard Overview Page

```python
import streamlit as st
from integrations import get_daily_metrics, get_vertical_breakdown
from utils import format_number, format_percentage

# Get metrics
metrics = get_daily_metrics()

# Display metric cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📧 Sent Today", format_number(metrics['sent_today']))
with col2:
    st.metric("📅 Sent This Week", format_number(metrics['sent_this_week']))
with col3:
    st.metric("📊 Sent This Month", format_number(metrics['sent_this_month']))
with col4:
    st.metric("💬 Response Rate", format_percentage(metrics['response_rate']))

# Vertical breakdown table
st.subheader("Performance by Vertical")
breakdown = get_vertical_breakdown()

for item in breakdown:
    st.write(f"**{item['vertical'].upper()}**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sent", format_number(item['sent_total']))
    with col2:
        st.metric("Sent Today", format_number(item['sent_today']))
    with col3:
        st.metric("Response Rate", format_percentage(item['response_rate']))
```

---

### 2. Prospect Upload Page

```python
import streamlit as st
import pandas as pd
from integrations import append_prospects, get_prospect_count
from utils import validate_prospect_csv, format_number

st.title("📥 Upload Prospects")

# Get list of verticals from database
from database import models
verticals = models.get_verticals(active_only=True)

# Create upload section for each vertical
for vertical in verticals:
    with st.expander(f"{vertical['display_name']} ({vertical['vertical_id']})"):
        # Show current count
        current_count = get_prospect_count(vertical['vertical_id'])
        st.info(f"Current prospects: {format_number(current_count)}")

        # File uploader
        uploaded_file = st.file_uploader(
            f"Upload CSV for {vertical['display_name']}",
            key=f"upload_{vertical['vertical_id']}",
            type=['csv']
        )

        if uploaded_file:
            # Read uploaded file
            df = pd.read_csv(uploaded_file)

            # Validate
            is_valid, error = validate_prospect_csv(df)

            if is_valid:
                # Show preview
                st.write("Preview (first 5 rows):")
                st.dataframe(df.head())

                # Confirm button
                if st.button(f"Add {len(df)} prospects", key=f"add_{vertical['vertical_id']}"):
                    # Add prospects
                    count_added = append_prospects(vertical['vertical_id'], df)
                    st.success(f"✅ Added {count_added} new prospects!")
                    st.info(f"Total prospects: {format_number(current_count + count_added)}")
            else:
                st.error(f"❌ Invalid CSV: {error}")
```

---

### 3. Prospect Viewer Page

```python
import streamlit as st
from integrations import read_prospects, get_prospect_stats
from utils import format_number

st.title("👥 View Prospects")

# Get verticals
from database import models
verticals = models.get_verticals(active_only=True)

# Vertical selector
selected_vertical = st.selectbox(
    "Select Vertical",
    options=[v['vertical_id'] for v in verticals],
    format_func=lambda x: next(v['display_name'] for v in verticals if v['vertical_id'] == x)
)

# Get prospect stats
stats = get_prospect_stats(selected_vertical)

# Display stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total", format_number(stats['total']))
with col2:
    st.metric("Not Contacted", format_number(stats['not_contacted']))
with col3:
    st.metric("Initial Sent", format_number(stats['initial_sent']))
with col4:
    st.metric("Followup Sent", format_number(stats['followup_sent']))

# Read prospects
df = read_prospects(selected_vertical)

if not df.empty:
    # Add search
    search = st.text_input("🔍 Search by email or company")

    if search:
        mask = (
            df['email'].str.contains(search, case=False, na=False) |
            df['company_name'].str.contains(search, case=False, na=False)
        )
        df = df[mask]

    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        height=500
    )

    # Export button
    if st.button("📥 Export to CSV"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{selected_vertical}_prospects.csv",
            mime="text/csv"
        )
else:
    st.info("No prospects found for this vertical.")
```

---

### 4. Campaign Status Page

```python
import streamlit as st
from integrations import get_allocation_status, get_daily_summary
from utils import format_number, format_percentage, format_status_badge

st.title("📅 Campaign Status")

# Get coordination status
status = get_allocation_status()

# Display date and last updated
st.write(f"**Date:** {status['date']}")
st.write(f"**Last Updated:** {status['last_updated']}")

# Overall capacity
st.header("Overall Capacity")
total_capacity = status['total_capacity']
total_sent = status['total_sent']
total_remaining = status['total_remaining']

progress = total_sent / total_capacity if total_capacity > 0 else 0
st.progress(progress)
st.write(f"{format_number(total_sent)} / {format_number(total_capacity)} sent ({format_percentage(progress)})")

# Initial campaign
st.header("Initial Outreach")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Allocated", format_number(status['initial']['allocated']))
with col2:
    st.metric("Sent", format_number(status['initial']['sent']))
with col3:
    st.metric("Remaining", format_number(status['initial']['remaining']))
with col4:
    st.write(format_status_badge(status['initial']['status']))

# Followup campaign
st.header("Follow-up Campaign")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Allocated", format_number(status['followup']['allocated']))
with col2:
    st.metric("Sent", format_number(status['followup']['sent']))
with col3:
    st.metric("Remaining", format_number(status['followup']['remaining']))
with col4:
    st.write(format_status_badge(status['followup']['status']))

# Text summary
st.subheader("Summary")
summary = get_daily_summary()
st.text(summary)
```

---

### 5. Sent Email History Page

```python
import streamlit as st
from integrations import read_sent_tracker, get_sent_by_date
from utils import format_number, format_date
import plotly.express as px

st.title("📨 Sent Email History")

# Read sent tracker
sent_df = read_sent_tracker()

if not sent_df.empty:
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sent", format_number(len(sent_df)))
    with col2:
        success_count = len(sent_df[sent_df['status'] == 'SUCCESS'])
        st.metric("Successful", format_number(success_count))
    with col3:
        error_count = len(sent_df[sent_df['status'] != 'SUCCESS'])
        st.metric("Errors", format_number(error_count))

    # Line chart - emails over time
    st.subheader("Emails Sent Over Time")
    daily_df = get_sent_by_date()

    if not daily_df.empty:
        fig = px.line(
            daily_df,
            x='date',
            y='count',
            title='Daily Email Volume',
            labels={'date': 'Date', 'count': 'Emails Sent'}
        )
        st.plotly_chart(fig, use_container_width=True)

    # Filters
    st.subheader("Filter Emails")
    col1, col2 = st.columns(2)

    with col1:
        vertical_filter = st.selectbox(
            "Vertical",
            options=['All'] + list(sent_df['vertical'].unique())
        )

    with col2:
        type_filter = st.selectbox(
            "Message Type",
            options=['All', 'initial', 'followup']
        )

    # Apply filters
    filtered_df = sent_df.copy()

    if vertical_filter != 'All':
        filtered_df = filtered_df[filtered_df['vertical'] == vertical_filter]

    if type_filter != 'All':
        filtered_df = filtered_df[filtered_df['message_type'] == type_filter]

    # Display table
    st.dataframe(
        filtered_df[['timestamp', 'email', 'vertical', 'message_type', 'subject_line', 'status']],
        use_container_width=True,
        height=400
    )
else:
    st.info("No sent emails yet.")
```

---

## Function Reference

### CSV Handler Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `read_prospects(vertical_id)` | vertical_id: str | pd.DataFrame | Read prospects CSV |
| `append_prospects(vertical_id, new_df)` | vertical_id: str, new_df: DataFrame | int | Add prospects, returns count added |
| `get_prospect_count(vertical_id)` | vertical_id: str | int | Count prospects |
| `get_prospect_stats(vertical_id, sent_df)` | vertical_id: str, sent_df: DataFrame (optional) | dict | Get statistics |

### Tracker Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `read_sent_tracker()` | None | pd.DataFrame | Read sent emails |
| `read_response_tracker()` | None | pd.DataFrame | Read responses |
| `get_daily_metrics(date)` | date: datetime (optional) | dict | Get metrics for date |
| `get_vertical_breakdown()` | None | list[dict] | Get stats by vertical |
| `get_sent_by_date(vertical)` | vertical: str (optional) | pd.DataFrame | Daily counts |
| `calculate_response_rate(vertical)` | vertical: str (optional) | float | Response rate (0.0-1.0) |

### Coordination Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `read_coordination()` | None | dict | Raw coordination data |
| `get_allocation_status()` | None | dict | Status with calculated fields |
| `get_daily_summary()` | None | str | Human-readable summary |
| `is_capacity_available()` | None | bool | Check if capacity remains |

### Formatter Functions

| Function | Parameters | Returns | Example |
|----------|------------|---------|---------|
| `format_number(num)` | num: int | str | "1,234" |
| `format_percentage(value, decimals)` | value: float, decimals: int | str | "12.5%" |
| `format_date(dt)` | dt: datetime | str | "Nov 04, 2025" |
| `format_time_ago(dt)` | dt: datetime | str | "2 hours ago" |
| `format_quota(used, total)` | used: int, total: int | str | "45 / 100 (45%)" |
| `format_status_badge(status)` | status: str | str | "✅ Active" |

### Validator Functions

| Function | Parameters | Returns | Description |
|----------|------------|---------|-------------|
| `validate_email(email)` | email: str | bool | Check email format |
| `validate_prospect_csv(df)` | df: DataFrame | (bool, str) | Validate prospect CSV |
| `validate_vertical_id(vertical_id)` | vertical_id: str | bool | Validate vertical ID format |

---

## Data Structures

### Daily Metrics Dictionary
```python
{
    'sent_today': 150,           # int
    'sent_this_week': 950,       # int
    'sent_this_month': 3200,     # int
    'response_rate': 0.125,      # float (0.0-1.0)
    'error_rate': 0.02           # float (0.0-1.0)
}
```

### Allocation Status Dictionary
```python
{
    'date': '2025-11-04',
    'last_updated': '2025-11-04T11:42:22.746794-05:00',
    'initial': {
        'allocated': 225,
        'sent': 150,
        'remaining': 75,
        'status': 'running'
    },
    'followup': {
        'allocated': 225,
        'sent': 0,
        'remaining': 225,
        'status': 'idle'
    },
    'total_capacity': 450,
    'total_sent': 150,
    'total_remaining': 300
}
```

### Vertical Breakdown List
```python
[
    {
        'vertical': 'debarment',
        'sent_total': 450,
        'sent_today': 75,
        'response_rate': 0.15
    },
    {
        'vertical': 'food_recall',
        'sent_total': 320,
        'sent_today': 60,
        'response_rate': 0.12
    }
]
```

### Prospect Stats Dictionary
```python
{
    'total': 1500,
    'not_contacted': 1200,
    'initial_sent': 200,
    'followup_sent': 80,
    'responded': 20
}
```

---

## Error Handling

All functions handle errors gracefully:

```python
# Missing files return empty/default data (no crash)
df = read_prospects('nonexistent_vertical')  # Returns empty DataFrame
metrics = get_daily_metrics()  # Returns zeros if no data

# Invalid data raises ValueError with message
try:
    append_prospects('vertical', invalid_df)
except ValueError as e:
    st.error(f"Invalid data: {str(e)}")

# File I/O errors raise IOError
try:
    df = read_prospects('vertical')
except IOError as e:
    st.error(f"File error: {str(e)}")
```

---

## Performance Tips

1. **Use caching for tracker data**
   ```python
   @st.cache_data(ttl=60)
   def get_metrics():
       return get_daily_metrics()
   ```

2. **Read prospects once per page load**
   ```python
   @st.cache_data
   def load_prospects(vertical_id):
       return read_prospects(vertical_id)
   ```

3. **Clear cache when data changes**
   ```python
   from integrations import clear_cache

   # After uploading prospects
   count = append_prospects(vertical_id, df)
   clear_cache()  # Force refresh on next read
   st.cache_data.clear()  # Clear Streamlit cache
   ```

---

## Need Help?

- **Full API documentation:** See `BACKEND_INTEGRATION_SUMMARY.md`
- **Test examples:** See `test_integration.py`
- **File locations:** See `utils/windows_paths.py`

**All integration functions are tested and working with real production data!** ✅
