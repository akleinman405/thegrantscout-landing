# PostgreSQL MCP Server Configuration

MCP server for direct database access from Claude Code.

## Configuration Location

The actual `.mcp.json` config file is in the **project root** (`~/Documents/TheGrantScout/.mcp.json`).
This is required - Claude Code only looks for `.mcp.json` in the project root.

## Connection Details

| Setting | Value |
|---------|-------|
| Server | @modelcontextprotocol/server-postgres |
| Host | localhost |
| Port | 5432 |
| Database | thegrantscout |
| Schema | f990_2025 |
| User | postgres |
| Mode | Read-only |

## Usage

After restarting Claude Code, you can:

1. Check status: `/mcp`
2. Query directly: "How many foundations are in dim_foundations?"
3. Explore schema: "What tables are in f990_2025?"

## Important Notes

- Always use schema prefix: `f990_2025.table_name`
- MCP is **read-only** - use Python/psycopg2 for write operations
- `.mcp.json` is in `.gitignore` (contains credentials)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Server not in /mcp | Restart Claude Code completely |
| Connection refused | `brew services start postgresql` |
| Auth failed | Check password in .mcp.json |
| Schema not found | Use `f990_2025.tablename` |

## Alternative Packages

If the official package has issues, consider:
- `postgres-mcp` (crystaldba) - More features, read/write support
- `pg-mcp` - Flexible connection options

---

*Setup date: 2025-12-24*
