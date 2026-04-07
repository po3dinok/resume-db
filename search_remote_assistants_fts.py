import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Бизнес-ассистенты и помощники (удалённо) через FTS5 ===\n")

# Use FTS5 to find matching rowids, then join with resumes table
cur.execute("""
    SELECT r.row_id, r.fio, r.city_clean, r.desired_position, r.schedule, r.employment
    FROM resumes r
    INNER JOIN resume_fts f ON r.row_id = f.rowid
    WHERE resume_fts MATCH 'ассистент OR помощник'
    AND r.is_duplicate = 0
""")
all_rows = cur.fetchall()

print(f"Всего ассистентов/помощников по FTS5: {len(all_rows)}")

# Filter for remote in Python
remote = []
for r in all_rows:
    sched = str(r[4]).lower() if r[4] else ''
    empl = str(r[5]).lower() if r[5] else ''
    if 'удален' in sched or 'удалён' in sched or 'удален' in empl or 'удалён' in empl:
        remote.append(r)

print(f"Готовы к удалёнке: {len(remote)}\n")

for r in remote:
    print(f"  ID={r[0]}, {r[1]}, {r[2]}")
    print(f"    {r[3]}")
    print()

conn.close()
