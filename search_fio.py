import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

# Exact search for Филиппов Дмитрий Сергеевич
cur.execute("""
    SELECT row_id, fio, city_clean, desired_position, phone, email, is_duplicate 
    FROM resumes 
    WHERE fio = 'Филиппов Дмитрий Сергеевич'
""")
rows = cur.fetchall()

if rows:
    for r in rows:
        dup = " (дубликат)" if r[6] else ""
        print(f"Найден! ID={r[0]}, ФИО={r[1]}, Город={r[2]}, Должность={r[3]}, Тел={r[4]}, Email={r[5]}{dup}")
else:
    # Try broader search
    cur.execute("""
        SELECT row_id, fio, city_clean, desired_position, phone, email, is_duplicate 
        FROM resumes 
        WHERE fio LIKE '%Филиппов Дмитрий Сергеевич%'
    """)
    rows = cur.fetchall()
    if rows:
        for r in rows:
            dup = " (дубликат)" if r[6] else ""
            print(f"Найден! ID={r[0]}, ФИО={r[1]}, Город={r[2]}, Должность={r[3]}, Тел={r[4]}, Email={r[5]}{dup}")
    else:
        print("Не найдено: Филиппов Дмитрий Сергеевич")
        print("\nВсе Филипповы Дмитрий в базе:")
        cur.execute("""
            SELECT row_id, fio, city_clean, desired_position, phone, email 
            FROM resumes 
            WHERE fio LIKE '%Филиппов%' AND fio LIKE '%Дмитрий%'
        """)
        for r in cur.fetchall():
            print(f"  ID={r[0]}, ФИО={r[1]}, Город={r[2]}, Должность={r[3]}, Email={r[5]}")

conn.close()
