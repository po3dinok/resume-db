import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

cur.execute("""
    SELECT row_id, fio, city_clean, desired_position, schedule, employment
    FROM resumes 
    WHERE desired_position LIKE '%ассистент%'
    AND is_duplicate = 0
    LIMIT 30
""")
rows = cur.fetchall()

print("=== Ассистенты ===\n")
for r in rows:
    remote = "🌍" if ("удален" in str(r[4]).lower() or "удален" in str(r[5]).lower()) else ""
    print(f"  {remote} ID={r[0]}, {r[1]}, {r[2]}, {r[3]}")
    print(f"    График: {r[4]}, Занятость: {r[5]}")
    print()

conn.close()
