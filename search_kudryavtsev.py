import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

cur.execute("""
    SELECT row_id, fio, city_clean, desired_position, phone, email, is_duplicate 
    FROM resumes 
    WHERE fio LIKE '%Кудрявцев%' AND fio LIKE '%Александр%'
""")
rows = cur.fetchall()

if rows:
    for r in rows:
        dup = " (дубликат)" if r[6] else ""
        print(f"✅ ID={r[0]}, ФИО={r[1]}, Город={r[2]}, Должность={r[3]}, Тел={r[4]}, Email={r[5]}{dup}")
else:
    print("❌ Кудрявцев Александр не найден в базе")

conn.close()
