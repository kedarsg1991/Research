# Recon - Bank & Invoice Reconciliation CLI for Freelancers

Reconcile your bank statements with invoices in seconds. Built for freelancers, by freelancers.

## The Problem

Every month, freelancers spend hours manually matching bank transactions to invoices. It's tedious, error-prone, and takes time away from billable work. Generic accounting software is overbuilt and expensive. Spreadsheets work until they don't.

## The Solution

Recon is a local CLI tool that does the matching for you:

1. Import your bank statement CSV
2. Import your invoices CSV
3. Recon automatically matches payments to invoices by amount + date
4. Get a clear report of what's matched, what's missing, and what needs attention

Everything runs locally on your machine. No server. No database. No domain. Your financial data never leaves your computer.

## What You Get

### Free Version
- 1 bank account
- Basic invoice matching
- Text reports
- Community support

### Pro Version ($19/month or $199/year)
- Unlimited bank accounts
- Advanced date tolerance for matching
- CSV export
- PDF tax-ready reports
- Full expense categorization
- Priority email support

## How It Works

```bash
# Install dependencies
pip install -r requirements.txt

# Import your data
python recon.py import-data bank.csv invoices.csv

# Match payments to invoices
python recon.py reconcile

# See the report
python recon.py report

# Export to CSV or PDF (Pro)
python recon.py report --output matches.csv --pdf report.pdf
```

## CSV Format

### Bank Statement
Required columns: Date, Description, Amount
Optional: Balance

```csv
Date,Description,Amount,Balance
2026-09-03,Client ABC - Website Design,-1500.00,11000.00
2026-09-05,Client XYZ - Consultation,-3000.00,8000.00
```

### Invoices
Required columns: InvoiceID, Client, Date, Amount
Optional: Status

```csv
InvoiceID,Client,Date,Amount,Status
INV-1001,ABC,2026-09-02,1500.00,Paid
INV-1002,XYZ,2026-09-04,3000.00,Paid
```

## Why Freelancers Love Recon

- **Fast**: Reconcile months of transactions in seconds
- **Private**: Your data stays on your machine
- **Simple**: No accounting degree required
- ** Affordable**: $19/month is less than the time it saves you
- **No subscriptions to manage**: Cancel anytime

## Sample Output

```
============================================================
  Recon - Reconciliation Report
  2026-09-16 16:56
============================================================

  Total Bank Transactions:  $-14,569.49
  Total Invoices:           $17,500.00
  Matched Pairs:            6
  Unmatched Bank Txns:      5
  Unmatched Invoices:       1

  Recent Matches:
  2026-09-03 | Client ABC - Website Design    | $-1500.00 -> INV-1001
  2026-09-05 | Client XYZ - Consultation      | $-3000.00 -> INV-1002

  Expense Categories:
  Income         : $13200.00
  Software       : $  860.99
  Withdrawal     : $ 500.00
  Food           : $    8.50

  Unmatched Invoices (need payment):
  INV-1007 | PQR             | $ 3500.00 | Unpaid

============================================================
```

## Requirements

- Python 3.6 or higher
- Windows, Mac, or Linux
- No internet connection needed (except license activation)

## Support

Email: support@recon.dev
Docs: recon.dev/docs

## FAQ

**Is my data safe?**
Yes. All data is stored in a local SQLite database on your machine. Nothing is uploaded to any server.

**Can I use it for business accounting?**
Recon is designed for freelancers to track income and expenses. For full business accounting, pair it with your accountant's software.

**What banks are supported?**
Any bank that can export transactions as CSV. Most banks support this.

**Do you offer a free trial?**
Yes - the free version includes basic reconciliation. Upgrade to Pro for advanced features.