import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== FTS5 поиск: ассистенты удалённо ===\n")

# FTS5 query
cur.execute("""
    SELECT rowid FROM resume_fts WHERE resume_fts MATCH 'ассистент'
""")
fts_ids = set(row[0] for row in cur.fetchall())
print(f"FTS5 нашёл 'ассистент': {len(fts_ids)} записей")

# Filter by remote using indexed lookups
remote_count = 0
remote_list = []
for rid in list(fts_ids)[:200]:
    cur.execute("""
        SELECT row_id, fio, city_clean, desired_position, schedule, employment
        FROM resumes WHERE row_id = ?
    """, (rid,))
    r = cur.fetchone()
    if r:
        sched = str(r[4]).lower() if r[4] else ''
        empl = str(r[5]).lower() if r[5] else ''
        if 'удален' in sched or 'удалён' in sched or 'удален' in empl or 'удалён' in empl:
            remote_count += 1
            remote_list.append(r)

print(f"Удалённо: {remote_count}\n")

for r in remote_list:
    print(f"  ID={r[0]}, {r[1]}, {r[2]}")
    print(f"    {r[3]}")

conn.close()
