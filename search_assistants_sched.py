import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db', timeout=10)
cur = conn.cursor()

# Use the schedule index which we know exists
cur.execute("""
    SELECT row_id, fio, city_clean, desired_position, schedule
    FROM resumes 
    WHERE schedule LIKE '%удален%'
    AND desired_position LIKE '%ассистент%'
    AND is_duplicate = 0
""")
rows = cur.fetchall()

print(f"📊 Бизнес-ассистенты удалённо: {len(rows)}\n")

for r in rows:
    print(f"  ID={r[0]}, {r[1]}, {r[2]}, {r[3]}")

conn.close()
