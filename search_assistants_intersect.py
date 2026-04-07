import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db', timeout=10)
cur = conn.cursor()

# Step 1: Get schedule index - find all rowids with 'удален' in schedule
cur.execute("SELECT row_id FROM resumes WHERE schedule LIKE '%удален%'")
schedule_ids = set(row[0] for row in cur.fetchall())
print(f"Со schedule='удаленная работа': {len(schedule_ids)}")

# Step 2: Get assistants
cur.execute("SELECT row_id FROM resumes WHERE desired_position LIKE '%ассистент%' AND is_duplicate = 0")
assistant_ids = [row[0] for row in cur.fetchall()]
print(f"Ассистентов: {len(assistant_ids)}")

# Step 3: Intersect
remote_assistant_ids = [rid for rid in assistant_ids if rid in schedule_ids]
print(f"Ассистенты удалённо: {len(remote_assistant_ids)}")

# Step 4: Get details
print("\n=== Список ===\n")
for rid in remote_assistant_ids[:30]:
    cur.execute("SELECT row_id, fio, city_clean, desired_position FROM resumes WHERE row_id = ?", (rid,))
    r = cur.fetchone()
    if r:
        print(f"  ID={r[0]}, {r[1]}, {r[2]}, {r[3]}")

if len(remote_assistant_ids) > 30:
    print(f"\n  ... и ещё {len(remote_assistant_ids) - 30}")

conn.close()
