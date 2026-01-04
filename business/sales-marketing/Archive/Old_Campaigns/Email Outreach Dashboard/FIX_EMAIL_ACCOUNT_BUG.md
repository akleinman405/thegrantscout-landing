# Fix Email Account Form Bug

## Problem
Getting error: `create_email_account() got an unexpected keyword argument 'email'`

## Root Cause
The form is passing `email=...` but the database function expects `email_address=...`

## Fix Required
Find where `models.create_email_account()` is called in the dashboard code (likely in `pages/3_📧_Email_Accounts.py` or `components/forms.py`) and change the parameter name:

**Change from:**
```python
models.create_email_account(
    email=email_value,  # ❌ WRONG
    ...
)
```

**Change to:**
```python
models.create_email_account(
    email_address=email_value,  # ✅ CORRECT
    ...
)
```

## Database Function Signature
```python
create_email_account(email_address, smtp_host, smtp_port, smtp_username, 
                     password_encrypted, display_name, daily_send_limit, active)
```

All parameters must match exactly as shown above.

## Files to Check
1. `pages/3_📧_Email_Accounts.py` - Form submission code
2. `components/forms.py` - Form component

Search for `create_email_account` and verify all parameter names match the database function.
