import sqlite3
conn = sqlite3.connect('recon.db')
print('foreign_keys pragma:', conn.execute('PRAGMA foreign_keys').fetchone()[0])
print('auto_vacuum:', conn.execute('PRAGMA auto_vacuum').fetchone())
conn.close()
