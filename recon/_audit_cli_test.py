import subprocess, os, tempfile, shutil, sqlite3

work = tempfile.mkdtemp()
db = os.path.join(work, 'test.db')

def run(args):
    r = subprocess.run(['python', 'recon.py'] + args + ['--db', db], capture_output=True, text=True, cwd='D:\\Research\\recon')
    return f"CMD: recon.py {args} --db {os.path.basename(db)}\nSTDOUT:\n{stdout(r)}\nSTDERR:\n{stderr(r)}\nRC: {r.returncode}"

def stdout(r): return r.stdout.strip() or '(empty)'
def stderr(r): return r.stderr.strip() or '(empty)'

# Test 1: Free user creates account via import-data --account (no Pro check in import_data)
print("=== TEST 1: Free user import-data --account 'Business Checking' ===")
print(run(['import-data', 'sample_bank.csv', 'sample_invoices.csv', '--account', 'Business Checking']))

print("\n=== TEST 1b: Check what accounts now exist ===")
c = sqlite3.connect(db); c.row_factory = sqlite3.Row
rows = c.execute('SELECT * FROM bank_accounts').fetchall()
for r in rows: print(dict(r))
print("\n=== TEST 1c: Check bank_transactions account assignment ===")
rows = c.execute('SELECT id, bank_account_id, date, description FROM bank_transactions').fetchall()
for r in rows[:5]: print(dict(r))
c.close()

# Test 2: reconcile non-existent account as Free user
print("\n=== TEST 2: reconcile --account 'Nonexistent' (Free user) ===")
print(run(['reconcile', '--account', 'Nonexistent']))

# Test 3: reconcile with tolerance -5 as Free user
print("\n=== TEST 3: reconcile --tolerance -5 (Free user) ===")
print(run(['reconcile', '--tolerance', '-5']))

# Test 4: report --output as Free user
print("\n=== TEST 4: report --output out.csv (Free user) ===")
print(run(['report', '--output', os.path.join(work, 'out.csv')]))

# Test 5: accounts --create as Free user
print("\n=== TEST 5: accounts --create 'Sneaky' (Free user) ===")
print(run(['accounts', '--create', 'Sneaky']))

# Test 6: summary --account as Free user
print("\n=== TEST 6: summary --account 'Business Checking' (Free user) ===")
print(run(['summary', '--account', 'Business Checking']))

# Test 7: report --account as Free user
print("\n=== TEST 7: report --account 'Business Checking' (Free user) ===")
print(run(['report', '--account', 'Business Checking']))

shutil.rmtree(work, ignore_errors=True)
