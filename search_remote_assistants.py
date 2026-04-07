import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Бизнес-ассистенты и помощники (удалённо) ===\n")

# Search broadly for assistant roles with remote work
cur.execute("""
    SELECT row_id, fio, city_clean, desired_position, schedule, employment
    FROM resumes 
    WHERE (
        desired_position LIKE '%бизнес%ассистент%' OR 
        desired_position LIKE '%ассистент%' OR
        desired_position LIKE '%помощник%' OR
        desired_position LIKE '%personal assistant%' OR
        desired_position LIKE '%executive assistant%'
    )
    AND (
        schedule LIKE '%удален%' OR schedule LIKE '%удалён%' OR
        employment LIKE '%удален%' OR employment LIKE '%удалён%'
    )
    AND is_duplicate = 0
    ORDER BY row_id
""")
rows = cur.fetchall()

print(f"Найдено: {len(rows)} кандидатов\n")

for r in rows:
    print(f"  ID={r[0]}, ФИО={r[1]}, Город={r[2]}")
    print(f"    Должность: {r[3]}")
    print(f"    График: {r[4]}")
    print(f"    Занятость: {r[5]}")
    print()

conn.close()
