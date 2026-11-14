import sqlite3

conn = sqlite3.connect('V2/data/projects.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
print('Tables:', tables)
for t in tables:
    c.execute(f"PRAGMA table_info({t[0]});")
    print(f"Schema {t[0]}:", [col[1] for col in c.fetchall()])

# Also let's check PRJ004, PRJ478, PRJ477, PRJ467, PRJ479, PRJ480, PRJ117, PRJ131, PRJ473
ids = ['PRJ004', 'PRJ478', 'PRJ477', 'PRJ467', 'PRJ479', 'PRJ480', 'PRJ117', 'PRJ131', 'PRJ473']
print("\n--- Checking target PRJ IDs ---")
for pid in ids:
    c.execute("SELECT * FROM projects WHERE project_id = ?", (pid,))
    row = c.fetchone()
    print(f"{pid}: {row}")
