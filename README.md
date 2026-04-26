# Expense Report MCP Server

An MCP (Model Context Protocol) server that turns Claude into an expense report assistant. Scan receipt images, track expenses, and generate reports — all through conversation.

## Tools

| Tool | Description |
|------|-------------|
| `scan_receipt` | Scan a receipt image (JPG/PNG) and extract data via OCR |
| `scan_receipt_folder` | Batch scan all receipt images in a folder |
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
- Tesseract OCR (`brew install tesseract` on macOS)
- Claude Desktop or Claude Code

### Install

```bash
git clone https://github.com/balaprav/expense-report-mcp.git
cd expense-report-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install "mcp[cli]" pytesseract Pillow
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

- "Scan this receipt" (with image path)
- "Scan all receipts in ~/Desktop/receipts/"
- "I spent $45.20 at Chipotle on March 15 for a team lunch"
- "Add a $230 Delta flight on April 1st for the NYC trip"
- "Show me my expense summary"
- "Generate a CSV report for the NYC project"
- "What's my total spending on meals?"

## Features

- **Receipt image scanning** — OCR with image preprocessing (contrast, sharpening, upscaling)
- **Batch scanning** — process an entire folder of receipts at once
- **Auto-categorization** — detects vendor and assigns category automatically
- **Project grouping** — tag expenses by trip or project
- **Report generation** — CSV for spreadsheets or formatted text
- **Full CRUD** — add, edit, delete, and list expenses
- Tracks tax, tips, and payment methods
- Supports JPG, PNG, TIFF, BMP, and WebP

## License

MIT
