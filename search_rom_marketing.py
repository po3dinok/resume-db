import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Директор по маркетингу / Руководитель отдела маркетинга ===\n")

cur.execute("""
    SELECT row_id, fio, city_clean, desired_position, skills, experience_and_education, is_duplicate
    FROM resumes 
    WHERE (
        desired_position LIKE '%директор по маркетингу%' OR 
        desired_position LIKE '%head of marketing%' OR
        desired_position LIKE '%руководитель отдела маркетинга%' OR
        desired_position LIKE '%директор по маркетингу, рекламе%' OR
        specialty LIKE '%директор по маркетингу%' OR
        specialty LIKE '%руководитель отдела маркетинга%'
    )
    AND is_duplicate = 0
    LIMIT 30
""")
rows = cur.fetchall()
if rows:
    print(f"Найдено: {len(rows)}\n")
    for r in rows:
        dup = " (дубликат)" if r[6] else ""
        print(f"  ID={r[0]}, ФИО={r[1]}, Город={r[2]}, Должность={r[3]}{dup}")
        exp_preview = str(r[5])[:200] if r[5] else ""
        if exp_preview:
            print(f"    Опыт: {exp_preview}")
        print()
else:
    print("❌ Не найдено")

conn.close()
