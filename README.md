# Expense Report MCP Server

An MCP (Model Context Protocol) server that turns Claude into an expense report assistant. Upload receipts, track expenses, and generate reports — all through conversation.

## Tools

| Tool | Description |
|------|-------------|
| `extract_receipt` | Parse receipt text and extract structured data |
| `add_expense` | Add an expense entry to the current report |
| `edit_expense` | Edit an existing expense entry |
| `delete_expense` | Delete an expense by ID |
| `list_expenses` | List all expenses with optional filters |
| `get_summary` | Get totals broken down by category |
| `generate_report` | Export as CSV or formatted text report |

## Setup

### Prerequisites
- Python 3.10+
- Claude Desktop or Claude Code

### Install

```bash
git clone https://github.com/balaprav/expense-report-mcp.git
cd expense-report-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install "mcp[cli]"
```

### Add to Claude Desktop

Edit your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "expense-report": {
      "command": "/path/to/expense-report-mcp/.venv/bin/python",
      "args": ["/path/to/expense-report-mcp/server.py"]
    }
  }
}
```

Replace `/path/to/` with your actual path.

### Add to Claude Code

```bash
claude mcp add expense-report -- /path/to/expense-report-mcp/.venv/bin/python /path/to/expense-report-mcp/server.py
```

## Usage

Once connected, just talk to Claude naturally:

- "I spent $45.20 at Chipotle on March 15 for a team lunch"
- "Add a $230 Delta flight on April 1st for the NYC trip"
- "Show me my expense summary"
- "Generate a CSV report for the NYC project"
- "What's my total spending on meals?"

## Features

- Auto-categorizes expenses by vendor name
- Groups expenses by project or trip
- Generates CSV reports ready for Google Sheets / Excel
- Tracks tax, tips, and payment methods
- Edit and delete expenses

## License

MIT
