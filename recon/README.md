# Recon - Bank & Invoice Reconciliation CLI

Reconcile your bank statements with invoices in seconds. Built for freelancers.

## Features

- Import bank statements and invoices from CSV
- Auto-match payments to invoices by amount + date
- Flag unmatched transactions
- Auto-categorize expenses
- Generate text, CSV, and PDF reports
- Multi-bank account support (Pro)
- Everything runs locally - no server, no database, no domain

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
# 1. Import your bank statement and invoices
python recon.py import-data bank.csv invoices.csv

# 2. Match payments to invoices
python recon.py reconcile

# 3. See the report
python recon.py report

# 4. Export to CSV or PDF (Pro)
python recon.py report --output matches.csv --pdf report.pdf
```

## Multi-Bank Accounts (Pro)

```bash
# Create a new bank account (Pro)
python recon.py accounts --create "Business Checking"

# List all accounts
python recon.py accounts

# Import to a specific account
python recon.py import-data bank.csv invoices.csv --account "Business Checking"

# Reconcile specific account
python recon.py reconcile --account "Business Checking"

# Report for specific account
python recon.py report --account "Business Checking" --output business.csv --pdf business.pdf
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

## Commands

| Command | Description |
|---------|-------------|
| `import-data` | Import bank and invoice CSV files |
| `reconcile` | Match payments to invoices |
| `report` | Generate summary report |
| `summary` | Quick one-line overview |
| `clear` | Reset all data |
| `accounts` | List or create bank accounts (Pro) |
| `activate` | Unlock Pro features with license key |
| `pro` | Check Pro status |

## Pro Features

Upgrade to unlock:
- Unlimited bank accounts
- CSV and PDF export
- Advanced date tolerance for matching
- Full tax categorization
- Priority support

Visit gumroad.com/recon for license keys.

## Sample Data

Try with the included sample files:
```bash
python recon.py import-data sample_bank.csv sample_invoices.csv
python recon.py reconcile
python recon.py report
```