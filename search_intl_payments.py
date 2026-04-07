import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Международные платежи / SWIFT / Валютный контроль ===\n")

cur.execute("""
    SELECT row_id, fio, city_clean, desired_position, skills, experience_and_education, relocation, is_duplicate
    FROM resumes 
    WHERE (
        experience_and_education LIKE '%международн%платеж%' OR 
        skills LIKE '%международн%платеж%' OR
        experience_and_education LIKE '%SWIFT%' OR
        skills LIKE '%SWIFT%' OR
        experience_and_education LIKE '%валютн%контроль%' OR
        skills LIKE '%валютн%контроль%' OR
        experience_and_education LIKE '%foreign payment%' OR
        experience_and_education LIKE '%跨境%' OR
        desired_position LIKE '%international payment%' OR
        specialty LIKE '%international payment%' OR
        experience_and_education LIKE '%foreign bank%' OR
        experience_and_education LIKE '%иностранный банк%'
    )
    AND is_duplicate = 0
    LIMIT 30
""")
rows = cur.fetchall()
if rows:
    print(f"Найдено: {len(rows)}\n")
    for r in rows:
        dup = " (дубликат)" if r[7] else ""
        print(f"  ID={r[0]}, ФИО={r[1]}, Город={r[2]}, Должность={r[3]}{dup}")
        print(f"    Навыки: {str(r[4])[:150]}")
        if r[5]:
            print(f"    Опыт: {r[5][:150]}")
        print(f"    Переезд: {r[6]}")
        print()
else:
    print("❌ Не найдено")

# Search for English B1+
print("\n=== Кандидаты с английским B1+ ===")
cur.execute("""
    SELECT row_id, fio, city_clean, desired_position, skills
    FROM resumes 
    WHERE (
        skills LIKE '%B1%' OR skills LIKE '%B2%' OR skills LIKE '%C1%' OR skills LIKE '%C2%' OR
        skills LIKE '%Upper%' OR skills LIKE '%Advanced%' OR skills LIKE '%Proficiency%'
    )
    AND is_duplicate = 0
    LIMIT 20
""")
rows = cur.fetchall()
if rows:
    for r in rows:
        print(f"  ID={r[0]}, ФИО={r[1]}, Город={r[2]}, Должность={r[3]}")
        print(f"    Навыки: {str(r[4])[:150]}")
        print()

conn.close()
