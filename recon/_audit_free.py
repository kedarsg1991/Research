import subprocess, os, tempfile, shutil, sqlite3

work = tempfile.mkdtemp()
db = os.path.join(work, 'test.db')
fakedhome = tempfile.mkdtemp()  # fake HOME with no license file => Free

env = dict(os.environ)
env['USERPROFILE'] = fakedhome
env['HOME'] = fakedhome

def run(args):
    r = subprocess.run(['python', 'recon.py'] + args + ['--db', db],
                       capture_output=True, text=True, cwd='D:\\Research\\recon', env=env)
    return f"CMD: recon.py {args}\nSTDOUT:\n{stdout(r)}\nSTDERR:\n{stderr(r)}\nRC: {r.returncode}"

def stdout(r): return r.stdout.strip() or '(empty)'
def stderr(r): return r.stderr.strip() or '(empty)'

# Confirm Free (pro) status
print("=== pro status (should be LOCKED) ===")
print(run(['pro']))

# TEST A: import-data --account as FREE user -> bypass?
print("\n=== TEST A: import-data --account 'Business Checking' (FREE user) ===")
print(run(['import-data', 'sample_bank.csv', 'sample_invoices.csv', '--account', 'Business Checking']))
print("\n--- accounts after ---")
c = sqlite3.connect(db); c.row_factory = sqlite3.Row
for r in c.execute('SELECT * FROM bank_accounts').fetchall(): print(dict(r))
print("--- first txn account id ---")
print(dict(c.execute('SELECT id, bank_account_id FROM bank_transactions LIMIT 1').fetchone()))
c.close()

# TEST B: accounts --create as FREE user
print("\n=== TEST B: accounts --create 'Sneaky' (FREE user) ===")
print(run(['accounts', '--create', 'Sneaky']))

# TEST C: reconcile --account as FREE user (should be blocked)
print("\n=== TEST C: reconcile --account 'Business Checking' (FREE user) ===")
print(run(['reconcile', '--account', 'Business Checking']))

# TEST D: report --account as FREE user (should be blocked)
print("\n=== TEST D: report --account 'Business Checking' (FREE user) ===")
print(run(['report', '--account', 'Business Checking']))

# TEST E: report --output as FREE user (should be blocked)
print("\n=== TEST E: report --output out.csv (FREE user) ===")
print(run(['report', '--output', os.path.join(work, 'out.csv')]))

# TEST F: report --pdf as FREE user (should be blocked)
print("\n=== TEST F: report --pdf out.pdf (FREE user) ===")
print(run(['report', '--pdf', os.path.join(work, 'out.pdf')]))

# TEST G: reconcile --tolerance 5 as FREE user (should be blocked)
print("\n=== TEST G: reconcile --tolerance 5 (FREE user) ===")
print(run(['reconcile', '--tolerance', '5']))

# TEST H: reconcile --tolerance 3 as FREE user (default, allowed)
print("\n=== TEST H: reconcile --tolerance 3 (FREE user, default) ===")
print(run(['reconcile', '--tolerance', '3']))

shutil.rmtree(work, ignore_errors=True)
shutil.rmtree(fakedhome, ignore_errors=True)
