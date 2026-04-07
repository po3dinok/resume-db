import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Казначеи / Международные платежи ===\n")

# Search by position/skills
cur.execute("""
    SELECT row_id, fio, city_clean, desired_position, skills, experience_and_education, is_duplicate
    FROM resumes 
    WHERE (
        desired_position LIKE '%казначей%' OR 
        specialty LIKE '%казначей%' OR
        desired_position LIKE '%международн%платеж%' OR 
        specialty LIKE '%международн%платеж%' OR
        skills LIKE '%международн%платеж%' OR
        desired_position LIKE '%SWIFT%' OR
        specialty LIKE '%SWIFT%' OR
        skills LIKE '%SWIFT%' OR
        desired_position LIKE '%foreign payment%' OR
        specialty LIKE '%foreign payment%' OR
        desired_position LIKE '%treasury%' OR
        specialty LIKE '%treasury%'
    )
    AND is_duplicate = 0
    LIMIT 20
""")
rows = cur.fetchall()
if rows:
    print(f"Найдено: {len(rows)}\n")
    for r in rows:
        dup = " (дубликат)" if r[6] else ""
        print(f"  ID={r[0]}, ФИО={r[1]}, Город={r[2]}, Должность={r[3]}{dup}")
        skills_preview = r[5][:100] if r[5] else ""
        if skills_preview:
            print(f"    Опыт: {skills_preview}")
else:
    print("❌ Не найдено казначеев / специалистов по международным платежам")

# Search in Yerevan/Armenia
print("\n=== Кандидаты в Ереване / Армения ===")
cur.execute("""
    SELECT row_id, fio, city_clean, desired_position, skills
    FROM resumes 
    WHERE (city LIKE '%Ереван%' OR city LIKE '%Армения%' OR city_clean LIKE '%Ереван%')
    AND is_duplicate = 0
    LIMIT 10
""")
rows = cur.fetchall()
if rows:
    for r in rows:
        print(f"  ID={r[0]}, ФИО={r[1]}, Город={r[2]}, Должность={r[3]}")
else:
    print("❌ Кандидатов в Ереване не найдено")

conn.close()
