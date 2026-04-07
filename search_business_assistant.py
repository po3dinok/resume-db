import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Бизнес-ассистенты (удалённо) ===\n")

cur.execute("""
    SELECT row_id, fio, city_clean, desired_position, schedule, employment, is_duplicate
    FROM resumes 
    WHERE (
        desired_position LIKE '%бизнес ассистент%' OR 
        desired_position LIKE '%бизнес-ассистент%' OR
        specialty LIKE '%бизнес ассистент%' OR
        specialty LIKE '%бизнес-ассистент%'
    )
    AND is_duplicate = 0
    LIMIT 20
""")
rows = cur.fetchall()

if rows:
    for r in rows:
        dup = " (дубликат)" if r[6] else ""
        remote = "✅ Удалённо" if ("удален" in str(r[4]).lower() or "удален" in str(r[5]).lower() or "удалён" in str(r[4]).lower() or "удалён" in str(r[5]).lower()) else ""
        print(f"  ID={r[0]}, ФИО={r[1]}, Город={r[2]}, Должность={r[3]}{dup}")
        if remote:
            print(f"    🌍 {remote}")
        print(f"    График: {r[4]}")
        print(f"    Занятость: {r[5]}")
        print()
else:
    print("❌ Не найдено")

conn.close()
