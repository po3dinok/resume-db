import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Бизнес-ассистенты (удалённо) ===\n")

# Simple indexed search
cur.execute("""
    SELECT row_id, fio, city_clean, desired_position
    FROM resumes 
    WHERE desired_position LIKE '%ассистент%'
    AND is_duplicate = 0
    LIMIT 50
""")
rows = cur.fetchall()

print(f"Найдено ассистентов: {len(rows)}\n")

for r in rows:
    print(f"  ID={r[0]}, {r[1]}, {r[2]}, {r[3]}")

conn.close()
