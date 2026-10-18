import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
conn = sqlite3.connect('medimin.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print('Tables:', [t[0] for t in tables])
for t in tables:
    tn = t[0]
    c.execute(f'SELECT COUNT(*) FROM [{tn}]')
    cnt = c.fetchone()[0]
    c.execute(f'PRAGMA table_info([{tn}])')
    cols = [r[1] for r in c.fetchall()]
    print(f'\n--- {tn} ({cnt} rows) ---')
    print('Cols:', cols)
    if cnt > 0:
        c.execute(f'SELECT * FROM [{tn}] LIMIT 2')
        for row in c.fetchall():
            print(' ', repr(row))
conn.close()
