# PROMPT: Configure PostgreSQL for Remote Access

**Date:** 2025-12-22  
**For:** Claude Code CLI (Mac)  
**Agent:** Builder

---

## Situation

PostgreSQL is installed on this Mac and contains the TheGrantScout database. Need to enable remote connections so Windows machine on the same local network can access the database.

---

## Tasks

### 1. Detect Environment
- Get current Mac username
- Get Mac's local IP address
- Detect local network range (e.g., 192.168.1.0/24)
- Find PostgreSQL config file locations (postgresql.conf, pg_hba.conf)
- Confirm PostgreSQL is installed and running

### 2. Prompt for Password
- Ask user to input the password they want to use for remote connections
- If postgres user already has a password, confirm they want to keep or change it

### 3. Backup Config Files
- Copy postgresql.conf to postgresql.conf.backup
- Copy pg_hba.conf to pg_hba.conf.backup

### 4. Update postgresql.conf
- Set `listen_addresses = '*'`
- Confirm `port = 5432`

### 5. Update pg_hba.conf
- Add line to allow connections from local network:
  ```
  host    all    all    [detected_network_range]    scram-sha-256
  ```

### 6. Set PostgreSQL Password
- Set password for postgres user (or current user) using the input provided

### 7. Restart PostgreSQL
- Use appropriate method (brew services, pg_ctl, or systemctl)

### 8. Verify Configuration
- Confirm PostgreSQL is listening on 0.0.0.0:5432
- Test local connection with new credentials

### 9. Output Connection Info
Create a file `WINDOWS_CONNECTION_INFO.txt` with:
```
Host: [Mac's IP]
Port: 5432
Database: postgres
User: [username]
Password: [as entered]

psql command:
psql -h [Mac's IP] -U [username] -d postgres

Python (psycopg2):
conn = psycopg2.connect(
    host="[Mac's IP]",
    port=5432,
    database="postgres",
    user="[username]",
    password="[password]"
)
```

---

## Outputs

| File | Location | Purpose |
|------|----------|---------|
| postgresql.conf.backup | Same as original | Rollback if needed |
| pg_hba.conf.backup | Same as original | Rollback if needed |
| WINDOWS_CONNECTION_INFO.txt | Current directory | Connection details for Windows |

---

## Notes

- If firewall is enabled on Mac, remind user to allow port 5432
- If PostgreSQL was installed via Homebrew, configs are typically in `/opt/homebrew/var/postgresql@XX/`
- If installed via Postgres.app, configs are in `~/Library/Application Support/Postgres/`
- Do not commit WINDOWS_CONNECTION_INFO.txt to git (contains password)

---

## Rollback

If something breaks:
```bash
cp postgresql.conf.backup postgresql.conf
cp pg_hba.conf.backup pg_hba.conf
brew services restart postgresql
```
