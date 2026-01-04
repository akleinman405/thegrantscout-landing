# Prompt 1: Schema & Database Structure

Review the database schema and structure for TheGrantScout project. I need a comprehensive summary to add to our CLAUDE.md file.

**Find and analyze:**
1. schema.sql - document all tables, columns, data types, and relationships
2. database_config.py - connection patterns and any helper functions
3. Any migration files (migration_*.sql)
4. Postgresql_Info.txt structure (without exposing credentials)

**Output a summary including:**
- Table-by-table breakdown with purpose, key columns, and data types
- Foreign key relationships (what links to what)
- Data conventions (how amounts stored, date formats, NULL handling)
- Any indexes or constraints worth noting
- Common connection pattern/snippet

**Format as a markdown section ready to paste into CLAUDE.md**
