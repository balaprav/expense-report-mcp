import json
import csv
import io
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("expense-report")

# In-memory store for expenses in the current session
expenses: list[dict] = []

# Category mapping for common vendors
VENDOR_CATEGORIES = {
    # Restaurants & Food
    "mcdonald": "Meals & Dining",
    "starbucks": "Meals & Dining",
    "chipotle": "Meals & Dining",
    "subway": "Meals & Dining",
    "doordash": "Meals & Dining",
    "uber eats": "Meals & Dining",
    "grubhub": "Meals & Dining",
    "panera": "Meals & Dining",
    "chick-fil-a": "Meals & Dining",
    "wendy": "Meals & Dining",
    "pizza": "Meals & Dining",
    "restaurant": "Meals & Dining",
    "cafe": "Meals & Dining",
    "diner": "Meals & Dining",
    "bistro": "Meals & Dining",
    "grill": "Meals & Dining",
    "sushi": "Meals & Dining",
    "taco": "Meals & Dining",
    "burger": "Meals & Dining",
    "coffee": "Meals & Dining",
    # Travel & Transport
    "uber": "Travel & Transport",
    "lyft": "Travel & Transport",
    "delta": "Travel & Transport",
    "united": "Travel & Transport",
    "american airlines": "Travel & Transport",
    "southwest": "Travel & Transport",
    "jetblue": "Travel & Transport",
    "hertz": "Travel & Transport",
    "enterprise": "Travel & Transport",
    "avis": "Travel & Transport",
    "marriott": "Travel & Transport",
    "hilton": "Travel & Transport",
    "hyatt": "Travel & Transport",
    "airbnb": "Travel & Transport",
    "expedia": "Travel & Transport",
    "parking": "Travel & Transport",
    "toll": "Travel & Transport",
    "gas": "Travel & Transport",
    "shell": "Travel & Transport",
    "chevron": "Travel & Transport",
    "exxon": "Travel & Transport",
    "bp ": "Travel & Transport",
    # Office & Supplies
    "staples": "Office Supplies",
    "office depot": "Office Supplies",
    "amazon": "Office Supplies",
    "best buy": "Office Supplies",
    "apple": "Office Supplies",
    # Software & Subscriptions
    "google": "Software & Subscriptions",
    "microsoft": "Software & Subscriptions",
    "adobe": "Software & Subscriptions",
    "slack": "Software & Subscriptions",
    "zoom": "Software & Subscriptions",
    "dropbox": "Software & Subscriptions",
    "github": "Software & Subscriptions",
    "aws": "Software & Subscriptions",
    "vercel": "Software & Subscriptions",
    "heroku": "Software & Subscriptions",
    # Utilities & Phone
    "at&t": "Utilities & Phone",
    "verizon": "Utilities & Phone",
    "t-mobile": "Utilities & Phone",
    "comcast": "Utilities & Phone",
    "spectrum": "Utilities & Phone",
}

DEFAULT_CATEGORIES = [
    "Meals & Dining",
    "Travel & Transport",
    "Office Supplies",
    "Software & Subscriptions",
    "Utilities & Phone",
    "Entertainment",
    "Professional Services",
    "Health & Wellness",
    "Education & Training",
    "Miscellaneous",
]


def _categorize(vendor: str) -> str:
    """Match a vendor name to a category."""
    vendor_lower = vendor.lower()
    for keyword, category in VENDOR_CATEGORIES.items():
        if keyword in vendor_lower:
            return category
    return "Miscellaneous"


def _next_id() -> int:
    return len(expenses) + 1


@mcp.tool()
def extract_receipt(receipt_text: str) -> str:
    """Extract structured data from receipt text. Paste or describe a receipt and this
    tool will parse out the vendor, date, items, tax, tip, and total. Returns a JSON
    object you can pass to add_expense.

    Args:
        receipt_text: The raw text from a receipt, or a description of the purchase
                      (e.g. "Starbucks $5.40 coffee March 15 2026")
    """
    # The LLM (Claude) will have already interpreted the receipt image/text
    # before calling this tool. We provide structure and guidance for extraction.
    return json.dumps({
        "instruction": (
            "Please extract the following fields from the receipt text provided "
            "and call add_expense with the extracted values:"
        ),
        "fields_to_extract": {
            "vendor": "Business/store name",
            "amount": "Total amount as a number (e.g. 42.50)",
            "date": "Date in YYYY-MM-DD format",
            "category": f"One of: {', '.join(DEFAULT_CATEGORIES)}",
            "description": "Brief description of what was purchased",
            "tax": "Tax amount if visible (optional)",
            "tip": "Tip amount if visible (optional)",
            "payment_method": "Cash, credit card, debit, etc. (optional)",
        },
        "receipt_text": receipt_text,
        "suggested_category": _categorize(receipt_text),
    }, indent=2)


@mcp.tool()
def add_expense(
    vendor: str,
    amount: float,
    date: str,
    category: str = "",
    description: str = "",
    tax: float = 0.0,
    tip: float = 0.0,
    payment_method: str = "",
    project: str = "",
) -> str:
    """Add an expense entry to the current report.

    Args:
        vendor: Business or store name
        amount: Total amount in dollars (e.g. 42.50)
        date: Date of expense in YYYY-MM-DD format
        category: Expense category (e.g. "Meals & Dining", "Travel & Transport").
                  Auto-detected if left blank.
        description: Brief description of the purchase
        tax: Tax amount (optional, default 0)
        tip: Tip amount (optional, default 0)
        payment_method: How it was paid — cash, credit card, etc. (optional)
        project: Project or trip name to group expenses (optional)
    """
    if not category:
        category = _categorize(vendor)

    expense = {
        "id": _next_id(),
        "vendor": vendor,
        "amount": round(amount, 2),
        "date": date,
        "category": category,
        "description": description,
        "tax": round(tax, 2),
        "tip": round(tip, 2),
        "payment_method": payment_method,
        "project": project,
        "added_at": datetime.now().isoformat(),
    }
    expenses.append(expense)

    total_so_far = sum(e["amount"] for e in expenses)
    return json.dumps({
        "status": "success",
        "message": f"Expense #{expense['id']} added: {vendor} — ${amount:.2f}",
        "expense": expense,
        "running_total": round(total_so_far, 2),
        "total_expenses": len(expenses),
    }, indent=2)


@mcp.tool()
def get_summary(project: str = "") -> str:
    """Get a summary of all expenses, with totals broken down by category.

    Args:
        project: Filter by project/trip name (optional — shows all if blank)
    """
    filtered = expenses
    if project:
        filtered = [e for e in expenses if e["project"].lower() == project.lower()]

    if not filtered:
        return json.dumps({"message": "No expenses recorded yet.", "total": 0})

    # Category totals
    by_category: dict[str, float] = {}
    for e in filtered:
        cat = e["category"]
        by_category[cat] = round(by_category.get(cat, 0) + e["amount"], 2)

    # Payment method totals
    by_payment: dict[str, float] = {}
    for e in filtered:
        pm = e["payment_method"] or "Not specified"
        by_payment[pm] = round(by_payment.get(pm, 0) + e["amount"], 2)

    total = round(sum(e["amount"] for e in filtered), 2)
    total_tax = round(sum(e["tax"] for e in filtered), 2)
    total_tip = round(sum(e["tip"] for e in filtered), 2)

    # Date range
    dates = sorted(e["date"] for e in filtered if e["date"])
    date_range = f"{dates[0]} to {dates[-1]}" if dates else "N/A"

    return json.dumps({
        "summary": {
            "total_expenses": len(filtered),
            "total_amount": total,
            "total_tax": total_tax,
            "total_tip": total_tip,
            "date_range": date_range,
            "by_category": dict(sorted(by_category.items(), key=lambda x: x[1], reverse=True)),
            "by_payment_method": by_payment,
        },
        "project_filter": project or "All",
    }, indent=2)


@mcp.tool()
def generate_report(project: str = "", format: str = "csv") -> str:
    """Generate a formatted expense report ready for download or copy-paste.

    Args:
        project: Filter by project/trip name (optional — includes all if blank)
        format: Output format — "csv" for spreadsheet-ready, or "text" for readable summary
    """
    filtered = expenses
    if project:
        filtered = [e for e in expenses if e["project"].lower() == project.lower()]

    if not filtered:
        return json.dumps({"message": "No expenses to report."})

    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "ID", "Date", "Vendor", "Description", "Category",
            "Amount", "Tax", "Tip", "Payment Method", "Project"
        ])
        for e in filtered:
            writer.writerow([
                e["id"], e["date"], e["vendor"], e["description"],
                e["category"], f"{e['amount']:.2f}", f"{e['tax']:.2f}",
                f"{e['tip']:.2f}", e["payment_method"], e["project"],
            ])

        # Add totals row
        total = sum(e["amount"] for e in filtered)
        total_tax = sum(e["tax"] for e in filtered)
        total_tip = sum(e["tip"] for e in filtered)
        writer.writerow([])
        writer.writerow([
            "", "", "", "", "TOTALS",
            f"{total:.2f}", f"{total_tax:.2f}", f"{total_tip:.2f}", "", ""
        ])

        return json.dumps({
            "format": "csv",
            "instructions": "Copy the CSV below and paste into Google Sheets or Excel",
            "csv_data": output.getvalue(),
            "total_expenses": len(filtered),
            "grand_total": round(total, 2),
        }, indent=2)

    else:
        # Text format
        lines = []
        lines.append("=" * 60)
        lines.append("EXPENSE REPORT")
        if project:
            lines.append(f"Project: {project}")
        dates = sorted(e["date"] for e in filtered if e["date"])
        if dates:
            lines.append(f"Period: {dates[0]} to {dates[-1]}")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 60)
        lines.append("")

        for e in filtered:
            lines.append(f"#{e['id']}  {e['date']}  {e['vendor']}")
            lines.append(f"     {e['description']}")
            lines.append(f"     Category: {e['category']}")
            amount_parts = [f"Amount: ${e['amount']:.2f}"]
            if e["tax"]:
                amount_parts.append(f"Tax: ${e['tax']:.2f}")
            if e["tip"]:
                amount_parts.append(f"Tip: ${e['tip']:.2f}")
            if e["payment_method"]:
                amount_parts.append(f"Paid: {e['payment_method']}")
            lines.append(f"     {' | '.join(amount_parts)}")
            lines.append("")

        lines.append("-" * 60)
        total = sum(e["amount"] for e in filtered)
        total_tax = sum(e["tax"] for e in filtered)
        total_tip = sum(e["tip"] for e in filtered)
        lines.append(f"TOTAL:  ${total:.2f}")
        if total_tax:
            lines.append(f"TAX:    ${total_tax:.2f}")
        if total_tip:
            lines.append(f"TIPS:   ${total_tip:.2f}")
        lines.append(f"GRAND:  ${total + total_tax + total_tip:.2f}")
        lines.append("=" * 60)

        return json.dumps({
            "format": "text",
            "report": "\n".join(lines),
            "total_expenses": len(filtered),
            "grand_total": round(total, 2),
        }, indent=2)


@mcp.tool()
def edit_expense(expense_id: int, **updates) -> str:
    """Edit an existing expense entry.

    Args:
        expense_id: The ID number of the expense to edit
        **updates: Fields to update — vendor, amount, date, category, description,
                   tax, tip, payment_method, project
    """
    for e in expenses:
        if e["id"] == expense_id:
            allowed = {"vendor", "amount", "date", "category", "description",
                       "tax", "tip", "payment_method", "project"}
            changed = []
            for key, value in updates.items():
                if key in allowed and value is not None:
                    old = e[key]
                    e[key] = value
                    changed.append(f"{key}: {old} → {value}")
            if changed:
                return json.dumps({
                    "status": "success",
                    "message": f"Expense #{expense_id} updated",
                    "changes": changed,
                    "expense": e,
                }, indent=2)
            else:
                return json.dumps({"status": "no_changes", "message": "No valid fields to update"})

    return json.dumps({"status": "error", "message": f"Expense #{expense_id} not found"})


@mcp.tool()
def delete_expense(expense_id: int) -> str:
    """Delete an expense entry by its ID.

    Args:
        expense_id: The ID number of the expense to delete
    """
    for i, e in enumerate(expenses):
        if e["id"] == expense_id:
            removed = expenses.pop(i)
            return json.dumps({
                "status": "success",
                "message": f"Deleted expense #{expense_id}: {removed['vendor']} — ${removed['amount']:.2f}",
                "remaining_expenses": len(expenses),
            }, indent=2)

    return json.dumps({"status": "error", "message": f"Expense #{expense_id} not found"})


@mcp.tool()
def list_expenses(project: str = "", category: str = "") -> str:
    """List all recorded expenses, optionally filtered by project or category.

    Args:
        project: Filter by project/trip name (optional)
        category: Filter by category (optional)
    """
    filtered = expenses
    if project:
        filtered = [e for e in filtered if e["project"].lower() == project.lower()]
    if category:
        filtered = [e for e in filtered if e["category"].lower() == category.lower()]

    if not filtered:
        return json.dumps({"message": "No expenses found matching your filters.", "expenses": []})

    return json.dumps({
        "expenses": filtered,
        "count": len(filtered),
        "total": round(sum(e["amount"] for e in filtered), 2),
    }, indent=2)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
