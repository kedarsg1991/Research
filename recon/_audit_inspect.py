import sqlite3, os, json

db = 'recon.db'
print('exists:', os.path.exists(db), 'size:', os.path.getsize(db) if os.path.exists(db) else 'N/A')
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
print('foreign_keys pragma:', conn.execute('PRAGMA foreign_keys').fetchone())
print()
for tbl in ['bank_accounts','bank_transactions','invoices','reconciliations']:
    cnt = conn.execute('SELECT COUNT(*) FROM ' + tbl).fetchone()[0]
    print('=== ' + tbl + ' (' + str(cnt) + ' rows) ===')
    rows = conn.execute('SELECT * FROM ' + tbl).fetchall()
    for r in rows:
        print(dict(r))
    print()

print('=== indexes on bank_transactions ===')
idx = conn.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND tbl_name='bank_transactions'").fetchall()
print([dict(i) for i in idx])

print('=== indexes on bank_accounts ===')
idx = conn.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND tbl_name='bank_accounts'").fetchall()
print([dict(i) for i in idx])

print('=== schema sql ===')
for row in conn.execute("SELECT type, name, sql FROM sqlite_master WHERE type IN ('table','index','trigger') ORDER BY type, name"):
    print(dict(row))

conn.close()
