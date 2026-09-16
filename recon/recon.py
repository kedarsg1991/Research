#!/usr/bin/env python3
"""Recon - Bank & Invoice Reconciliation CLI for Freelancers."""

import csv
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

import click

# ── Database Manager ──────────────────────────────────────────────
class Database:
    def __init__(self, db_path: str = "recon.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bank_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bank_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bank_account_id INTEGER NOT NULL DEFAULT 1,
                date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                balance REAL,
                category TEXT DEFAULT 'Uncategorized',
                FOREIGN KEY (bank_account_id) REFERENCES bank_accounts(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id TEXT UNIQUE NOT NULL,
                client TEXT NOT NULL,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                status TEXT DEFAULT 'Unpaid',
                matched INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reconciliations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bank_txn_id INTEGER,
                invoice_id INTEGER,
                matched_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bank_txn_id) REFERENCES bank_transactions(id),
                FOREIGN KEY (invoice_id) REFERENCES invoices(id)
            )
        """)
        # Insert default bank account if none exists
        conn.execute("INSERT OR IGNORE INTO bank_accounts (id, name) VALUES (1, 'Primary')")
        conn.commit()
        conn.close()

    def add_bank_transaction(self, date, description, amount, balance=None, category="Uncategorized", bank_account_id=1):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO bank_transactions (bank_account_id, date, description, amount, balance, category) VALUES (?, ?, ?, ?, ?, ?)",
            (bank_account_id, date, description, amount, balance, category)
        )
        conn.commit()
        conn.close()

    def add_bank_account(self, name: str, description: str = "") -> int:
        """Add a new bank account. Returns the account ID."""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                "INSERT INTO bank_accounts (name, description) VALUES (?, ?)",
                (name, description)
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Account with this name already exists, return its ID
            row = conn.execute("SELECT id FROM bank_accounts WHERE name = ?", (name,)).fetchone()
            return row[0] if row else 1
        finally:
            conn.close()

    def get_bank_accounts(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM bank_accounts ORDER BY name").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_bank_account(self, account_id: int) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM bank_accounts WHERE id = ?", (account_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def get_bank_account_by_name(self, name: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM bank_accounts WHERE name = ?", (name,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def add_invoice(self, invoice_id, client, date, amount, status="Unpaid"):
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                "INSERT INTO invoices (invoice_id, client, date, amount, status) VALUES (?, ?, ?, ?, ?)",
                (invoice_id, client, date, amount, status)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        conn.close()

    def get_all_bank_txns(self, bank_account_id: Optional[int] = None) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        if bank_account_id:
            rows = conn.execute("SELECT * FROM bank_transactions WHERE bank_account_id = ? ORDER BY date", (bank_account_id,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM bank_transactions ORDER BY date").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_all_invoices(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM invoices ORDER BY date").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def mark_matched(self, bank_txn_id: int, invoice_id: int):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO reconciliations (bank_txn_id, invoice_id) VALUES (?, ?)",
            (bank_txn_id, invoice_id)
        )
        conn.execute("UPDATE invoices SET matched = 1 WHERE id = ?", (invoice_id,))
        conn.commit()
        conn.close()

    def get_reconciled(self, bank_account_id: Optional[int] = None) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        if bank_account_id:
            rows = conn.execute("""
                SELECT r.id, r.bank_txn_id, r.invoice_id as rec_inv_id, r.matched_at,
                       bt.date as bank_date, bt.description as bank_desc, bt.amount as bank_amount,
                       i.invoice_id as inv_invoice_id, i.client, i.date as inv_date, i.amount as inv_amount
                FROM reconciliations r
                JOIN bank_transactions bt ON r.bank_txn_id = bt.id
                JOIN invoices i ON r.invoice_id = i.id
                WHERE bt.bank_account_id = ?
                ORDER BY r.matched_at DESC
            """, (bank_account_id,)).fetchall()
        else:
            rows = conn.execute("""
                SELECT r.id, r.bank_txn_id, r.invoice_id as rec_inv_id, r.matched_at,
                       bt.date as bank_date, bt.description as bank_desc, bt.amount as bank_amount,
                       i.invoice_id as inv_invoice_id, i.client, i.date as inv_date, i.amount as inv_amount
                FROM reconciliations r
                JOIN bank_transactions bt ON r.bank_txn_id = bt.id
                JOIN invoices i ON r.invoice_id = i.id
                ORDER BY r.matched_at DESC
            """).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def clear_all(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM bank_transactions")
        conn.execute("DELETE FROM invoices")
        conn.execute("DELETE FROM reconciliations")
        conn.execute("DELETE FROM bank_accounts WHERE id != 1")
        conn.execute("INSERT OR IGNORE INTO bank_accounts (id, name) VALUES (1, 'Primary')")
        conn.commit()
        conn.close()

    def get_summary(self, bank_account_id: Optional[int] = None) -> Dict:
        conn = sqlite3.connect(self.db_path)
        if bank_account_id:
            bank_total = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM bank_transactions WHERE bank_account_id = ?", (bank_account_id,)).fetchone()[0]
            unmatched_bank = conn.execute("SELECT COUNT(*) FROM bank_transactions WHERE bank_account_id = ? AND id NOT IN (SELECT bank_txn_id FROM reconciliations)", (bank_account_id,)).fetchone()[0]
        else:
            bank_total = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM bank_transactions").fetchone()[0]
            unmatched_bank = conn.execute("SELECT COUNT(*) FROM bank_transactions WHERE id NOT IN (SELECT bank_txn_id FROM reconciliations)").fetchone()[0]
        inv_total = conn.execute("SELECT COALESCE(SUM(amount), 0) FROM invoices").fetchone()[0]
        matched_count = conn.execute("SELECT COUNT(*) FROM reconciliations").fetchone()[0]
        unmatched_inv = conn.execute("SELECT COUNT(*) FROM invoices WHERE matched = 0").fetchone()[0]
        conn.close()
        return {
            'bank_total': bank_total,
            'invoice_total': inv_total,
            'matched_count': matched_count,
            'unmatched_bank': unmatched_bank,
            'unmatched_invoices': unmatched_inv,
        }


# ── CSV Importer ──────────────────────────────────────────────────
def _get_field(row, *names, default=''):
    """Get a field from a CSV row, trying multiple column name variants."""
    for name in names:
        val = row.get(name)
        if val is not None and str(val).strip():
            return str(val).strip()
    return default


def import_bank_csv(db: Database, filepath: str, bank_account_id: int = 1):
    """Import bank statement CSV."""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                date = _get_field(row, 'Date', 'date', 'Txn Date', 'Transaction Date', 'Posting Date')
                desc = _get_field(row, 'Description', 'description', 'Narration', 'Memo', 'Particulars')
                amount_str = _get_field(row, 'Amount', 'amount', 'Debit', 'Credit')
                balance_str = _get_field(row, 'Balance', 'balance', 'Running Balance', 'Avail Balance')

                if not date or not amount_str:
                    click.echo(f"  Warning: skipping row - missing required columns", err=True)
                    continue

                amount = float(amount_str)
                balance = float(balance_str) if balance_str else None
                db.add_bank_transaction(date, desc, amount, balance, bank_account_id=bank_account_id)
                count += 1
            except (ValueError, KeyError) as e:
                click.echo(f"  Warning: skipping row - {e}", err=True)
        click.echo(f"  Imported {count} bank transactions")


def import_invoices_csv(db: Database, filepath: str):
    """Import invoices CSV."""
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                inv_id = _get_field(row, 'InvoiceID', 'invoice_id', 'Invoice No', 'Invoice Number', 'ID')
                client = _get_field(row, 'Client', 'client', 'Customer', 'customer', 'Party')
                date = _get_field(row, 'Date', 'date', 'Invoice Date', 'Due Date')
                amount_str = _get_field(row, 'Amount', 'amount', 'Total', 'Invoice Amount')
                status = _get_field(row, 'Status', 'status', 'Payment Status', 'Paid', 'Unpaid')

                if not inv_id or not amount_str:
                    click.echo(f"  Warning: skipping row - missing required columns", err=True)
                    continue

                amount = float(amount_str)
                db.add_invoice(inv_id, client, date, amount, status)
                count += 1
            except (ValueError, KeyError) as e:
                click.echo(f"  Warning: skipping row - {e}", err=True)
        click.echo(f"  Imported {count} invoices")


# ── Reconciliation Engine ─────────────────────────────────────────
def run_reconcile(db: Database, tolerance_days: int = 3, bank_account_id: Optional[int] = None):
    """Match bank transactions to invoices by amount + date proximity."""
    bank_txns = db.get_all_bank_txns(bank_account_id)
    invoices = db.get_all_invoices()

    pending_invoices = [inv for inv in invoices if inv['matched'] == 0]
    reconciled_bank_ids = {r['bank_txn_id'] for r in db.get_reconciled()}
    unmatched_bank = [txn for txn in bank_txns if txn['id'] not in reconciled_bank_ids]

    matched = 0
    for txn in unmatched_bank:
        txn_amount = abs(txn['amount'])
        try:
            txn_date = datetime.strptime(txn['date'], '%Y-%m-%d')
        except ValueError:
            continue

        for inv in pending_invoices:
            if abs(inv['amount'] - txn_amount) < 0.01:
                try:
                    inv_date = datetime.strptime(inv['date'], '%Y-%m-%d')
                except ValueError:
                    continue
                if abs((inv_date - txn_date).days) <= tolerance_days:
                    db.mark_matched(txn['id'], inv['id'])
                    matched += 1
                    pending_invoices.remove(inv)
                    break

    return matched


# ── Categorization ────────────────────────────────────────────────
CATEGORIES = {
    'Software': ['aws', 'amazon', 'netflix', 'github', 'adobe', 'slack', 'zoom',
                 'notion', 'hosting', 'cloud', 'digitalocean', 'linode', 'firebase'],
    'Food': ['starbucks', 'coffee', 'restaurant', 'cafe', 'lunch', 'dinner', 'food',
             'swiggy', 'zomato', 'domino', 'pizza'],
    'Travel': ['uber', 'lyft', 'gas', 'flight', 'hotel', 'train', 'metro', 'ola', 'rapido'],
    'Office': ['office', 'supplies', 'stationery', 'printer', 'paper', 'stapler'],
    'Entertainment': ['netflix', 'spotify', 'youtube', 'game', 'movie', 'hotstar', 'prime'],
    'Withdrawal': ['atm', 'withdrawal', 'cash'],
    'Income': ['invoice', 'payment', 'salary', 'transfer', 'refund', 'credit'],
    'Contractor': ['client', 'contractor', 'freelancer', 'subcontractor'],
}

def categorize(description: str) -> str:
    """Auto-categorize a transaction based on description keywords."""
    desc_lower = description.lower()
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in desc_lower:
                return category
    return 'Uncategorized'


# ── Reporting ─────────────────────────────────────────────────────
def generate_report(db: Database, bank_account_id: Optional[int] = None):
    """Generate a summary report."""
    summary = db.get_summary(bank_account_id)
    reconciled = db.get_reconciled(bank_account_id)

    click.echo("\n" + "=" * 60)
    click.echo("  Recon - Reconciliation Report")
    click.echo("  " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    if bank_account_id:
        acc = db.get_bank_account(bank_account_id)
        click.echo(f"  Account: {acc['name']}")
    click.echo("=" * 60)

    click.echo(f"\n  Total Bank Transactions:  ${summary['bank_total']:,.2f}")
    click.echo(f"  Total Invoices:           ${summary['invoice_total']:,.2f}")
    click.echo(f"  Matched Pairs:            {summary['matched_count']}")
    click.echo(f"  Unmatched Bank Txns:      {summary['unmatched_bank']}")
    click.echo(f"  Unmatched Invoices:       {summary['unmatched_invoices']}")

    if reconciled:
        click.echo(f"\n  Recent Matches:")
        for r in reconciled[:10]:
            click.echo(f"  {r['bank_date']} | {r['bank_desc'][:30]:30s} | ${r['bank_amount']:8.2f} -> {r['inv_invoice_id']}")

    bank_txns = db.get_all_bank_txns(bank_account_id)
    categories = {}
    for txn in bank_txns:
        cat = categorize(txn['description'])
        categories[cat] = categories.get(cat, 0.0) + abs(txn['amount'])

    click.echo(f"\n  Expense Categories:")
    for cat, total in sorted(categories.items(), key=lambda x: -x[1]):
        bar = "#" * min(int(total / 50), 40)
        click.echo(f"  {cat:15s}: ${total:8.2f} {bar}")

    unmatched_invoices = [inv for inv in db.get_all_invoices() if inv['matched'] == 0]
    if unmatched_invoices:
        click.echo(f"\n  Unmatched Invoices (need payment):")
        for inv in unmatched_invoices:
            click.echo(f"  {inv['invoice_id']} | {inv['client']:15s} | ${inv['amount']:8.2f} | {inv['status']}")

    click.echo("\n" + "=" * 60)


def export_csv(db: Database, output_path: str, bank_account_id: Optional[int] = None):
    """Export reconciliation results to CSV."""
    reconciled = db.get_reconciled(bank_account_id)
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Bank Date', 'Description', 'Amount', 'Invoice ID', 'Client', 'Invoice Date'])
        for r in reconciled:
            writer.writerow([
                r['bank_date'], r['bank_desc'], r['bank_amount'],
                r['inv_invoice_id'], r['client'], r['inv_date']
            ])
    click.echo(f"  Exported {len(reconciled)} matches to {output_path}")


def export_pdf(db: Database, output_path: str, bank_account_id: Optional[int] = None):
    """Export reconciliation report to PDF."""
    try:
        from fpdf import FPDF
    except ImportError:
        click.echo("  Error: fpdf2 not installed. Run: pip install fpdf2", err=True)
        return

    summary = db.get_summary(bank_account_id)
    reconciled = db.get_reconciled(bank_account_id)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Recon - Reconciliation Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, datetime.now().strftime("%Y-%m-%d"), new_x="LMARGIN", new_y="NEXT", align="C")
    if bank_account_id:
        acc = db.get_bank_account(bank_account_id)
        pdf.cell(0, 8, f"Account: {acc['name']}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Total Bank Transactions: ${summary['bank_total']:,.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Total Invoices: ${summary['invoice_total']:,.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Matched Pairs: {summary['matched_count']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Unmatched Bank Transactions: {summary['unmatched_bank']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Unmatched Invoices: {summary['unmatched_invoices']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    if reconciled:
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Matched Transactions", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        for r in reconciled:
            line = f"{r['bank_date']} | {r['bank_desc'][:30]} | ${r['bank_amount']:.2f} -> {r['inv_invoice_id']}"
            pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")

    pdf.output(output_path)
    click.echo(f"  Exported PDF report to {output_path}")


# ── License Check ─────────────────────────────────────────────────
PRO_LICENSES_FILE = Path.home() / ".recon_pro_licenses.txt"

def is_pro_enabled() -> bool:
    """Check if Pro features are unlocked via license key."""
    if not PRO_LICENSES_FILE.exists():
        return False
    try:
        with open(PRO_LICENSES_FILE, 'r') as f:
            keys = [line.strip() for line in f if line.strip()]
        return len(keys) > 0
    except Exception:
        return False

def activate_license(key: str) -> bool:
    """Activate a Pro license key."""
    valid_keys = ["RECON-PRO-2026-DEMO", "RECON-PRO-LIFETIME-001"]
    if key in valid_keys:
        PRO_LICENSES_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PRO_LICENSES_FILE, 'w') as f:
            f.write(key + "\n")
        return True
    return False


# ── CLI Commands ──────────────────────────────────────────────────
@click.group()
@click.version_option(version="1.0.0", prog_name="recon")
def cli():
    """Recon - Bank & Invoice Reconciliation for Freelancers."""
    pass


@cli.command()
@click.argument('bank_csv', type=click.Path(exists=True))
@click.argument('invoices_csv', type=click.Path(exists=True))
@click.option('--db', default='recon.db', help='Database file path')
@click.option('--account', default='Primary', help='Bank account name (Pro feature)')
def import_data(bank_csv, invoices_csv, db, account):
    """Import bank statement and invoice CSV files."""
    database = Database(db)
    
    # Get or create bank account
    account_id = database.add_bank_account(account)
    
    click.echo(f"Importing bank statement to account '{account}'...")
    import_bank_csv(database, bank_csv, account_id)
    click.echo("Importing invoices...")
    import_invoices_csv(database, invoices_csv)
    click.echo(f"\nDone! Run 'recon reconcile --db {db}' to match them.")


@cli.command(name='reconcile')
@click.option('--db', default='recon.db', help='Database file path')
@click.option('--tolerance', default=3, help='Date tolerance in days for matching (Pro: unlimited)')
@click.option('--account', default=None, help='Bank account name to reconcile (Pro feature)')
def reconcile_cmd(db, tolerance, account):
    """Match bank transactions to invoices."""
    database = Database(db)
    
    # Check Pro for advanced tolerance
    if tolerance != 3 and not is_pro_enabled():
        click.echo("  Advanced date tolerance requires Pro. Use --tolerance 3 or upgrade.", err=True)
        return
    
    account_id = None
    if account:
        if not is_pro_enabled():
            click.echo("  Multi-account reconciliation requires Pro.", err=True)
            return
        acc = database.get_bank_account_by_name(account)
        if not acc:
            click.echo(f"  Account '{account}' not found.", err=True)
            return
        account_id = acc['id']
    
    click.echo("Reconciling...")
    matched = run_reconcile(database, tolerance, account_id)
    click.echo(f"  Matched {matched} transactions")


@cli.command()
@click.option('--db', default='recon.db', help='Database file path')
@click.option('--output', default=None, help='Export CSV file path (Pro feature)')
@click.option('--pdf', default=None, help='Export PDF report path (Pro feature)')
@click.option('--account', default=None, help='Bank account name to filter (Pro feature)')
def report(db, output, pdf, account):
    """Generate reconciliation report."""
    database = Database(db)
    
    if account:
        if not is_pro_enabled():
            click.echo("  Account filtering requires Pro.", err=True)
            return
        acc = database.get_bank_account_by_name(account)
        if not acc:
            click.echo(f"  Account '{account}' not found.", err=True)
            return
        account_id = acc['id']
    else:
        account_id = None
    
    generate_report(database, account_id)
    
    if output:
        if not is_pro_enabled():
            click.echo("  CSV export requires Pro.", err=True)
        else:
            export_csv(database, output, account_id)
    
    if pdf:
        if not is_pro_enabled():
            click.echo("  PDF export requires Pro.", err=True)
        else:
            export_pdf(database, pdf, account_id)


@cli.command()
@click.option('--db', default='recon.db', help='Database file path')
@click.option('--account', default=None, help='Bank account name to filter (Pro feature)')
def summary(db, account):
    """Show quick summary."""
    database = Database(db)
    
    if account:
        if not is_pro_enabled():
            click.echo("  Account filtering requires Pro.", err=True)
            return
        acc = database.get_bank_account_by_name(account)
        if not acc:
            click.echo(f"  Account '{account}' not found.", err=True)
            return
        account_id = acc['id']
    else:
        account_id = None
    
    s = database.get_summary(account_id)
    if account_id:
        click.echo(f"Account: {account} | Bank: ${s['bank_total']:,.2f} | Invoices: ${s['invoice_total']:,.2f} | Matched: {s['matched_count']}")
    else:
        click.echo(f"Bank: ${s['bank_total']:,.2f} | Invoices: ${s['invoice_total']:,.2f} | Matched: {s['matched_count']}")


@cli.command()
@click.option('--db', default='recon.db', help='Database file path')
def clear(db):
    """Clear all data from the database."""
    database = Database(db)
    database.clear_all()
    click.echo("  All data cleared")


@cli.command()
@click.option('--db', default='recon.db', help='Database file path')
@click.option('--create', default=None, help='Create a new bank account (Pro feature)')
def accounts(db, create):
    """List or create bank accounts."""
    database = Database(db)
    
    if create:
        if not is_pro_enabled():
            click.echo("  Creating accounts requires Pro.", err=True)
            return
        account_id = database.add_bank_account(create)
        click.echo(f"  Created account '{create}' (ID: {account_id})")
        return
    
    accounts_list = database.get_bank_accounts()
    if not accounts_list:
        click.echo("  No bank accounts found.")
        return
    
    click.echo("\n  Bank Accounts:")
    for acc in accounts_list:
        # Get transaction count for this account
        conn = sqlite3.connect(db)
        count = conn.execute("SELECT COUNT(*) FROM bank_transactions WHERE bank_account_id = ?", (acc['id'],)).fetchone()[0]
        conn.close()
        pro_marker = " (Pro)" if acc['id'] != 1 else ""
        click.echo(f"  {acc['name']}{pro_marker} - {count} transactions")


@cli.command()
@click.argument('license_key')
def activate(license_key):
    """Activate a Pro license key."""
    if activate_license(license_key):
        click.echo("  Pro features unlocked!")
    else:
        click.echo("  Invalid license key.", err=True)


@cli.command()
def pro():
    """Check Pro status and upgrade info."""
    if is_pro_enabled():
        click.echo("  Pro features: ACTIVE")
    else:
        click.echo("  Pro features: LOCKED")
        click.echo("\n  Upgrade to Pro for:")
        click.echo("  - Unlimited bank accounts")
        click.echo("  - CSV + PDF export")
        click.echo("  - Advanced date tolerance")
        click.echo("  - Full tax categorization")
        click.echo("\n  Visit: gumroad.com/recon")


if __name__ == '__main__':
    cli()