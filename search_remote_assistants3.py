import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Бизнес-ассистенты и помощники (удалённо) ===\n")

# Get all assistants first
cur.execute("""
    SELECT row_id, fio, city_clean, desired_position, schedule, employment
    FROM resumes 
    WHERE desired_position LIKE '%ассистент%'
    AND is_duplicate = 0
""")
all_rows = cur.fetchall()

# Filter for remote
remote = []
for r in all_rows:
    sched = str(r[4]).lower() if r[4] else ''
    empl = str(r[5]).lower() if r[5] else ''
    if 'удален' in sched or 'удалён' in sched or 'удален' in empl or 'удалён' in empl:
        remote.append(r)

print(f"Всего ассистентов: {len(all_rows)}")
print(f"Готовы к удалёнке: {len(remote)}\n")

for r in remote:
    print(f"  ID={r[0]}, {r[1]}, {r[2]}")
    print(f"    {r[3]}")
    print()

conn.close()
