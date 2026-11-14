import sqlite3

conn = sqlite3.connect('data/stage2/projects.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = c.fetchall()
print('Tables in data/stage2/projects.db:', tables)

ids = ['PRJ004', 'PRJ478', 'PRJ477', 'PRJ467', 'PRJ479', 'PRJ480', 'PRJ117', 'PRJ131', 'PRJ473']
for pid in ids:
    c.execute("SELECT * FROM projects WHERE project_id = ?", (pid,))
    row = c.fetchone()
    print(f"{pid}: {row}")
