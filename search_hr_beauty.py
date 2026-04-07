import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== HR специалисты в Москве (Beauty/Retail) ===\n")

# Search for HR roles in Moscow with beauty/retail keywords
cur.execute("""
    SELECT row_id, fio, city_clean, desired_position, skills, experience_and_education, is_duplicate
    FROM resumes 
    WHERE (
        desired_position LIKE '%HR%' OR 
        desired_position LIKE '%HR-менеджер%' OR
        desired_position LIKE '%HR-специалист%' OR
        desired_position LIKE '%HRBP%' OR
        desired_position LIKE '%менеджер по персоналу%' OR
        desired_position LIKE '%специалист по персоналу%' OR
        desired_position LIKE '%рекрутер%'
    )
    AND (
        city_clean = 'Москва' OR city LIKE '%Москва%'
    )
    AND (
        skills LIKE '%бьюти%' OR skills LIKE '%красота%' OR skills LIKE '%косметик%' OR 
        skills LIKE '%салон%' OR skills LIKE '%парикмахер%' OR skills LIKE '%ретейл%' OR
        skills LIKE '%ритейл%' OR skills LIKE '%магазин%' OR skills LIKE '%торговля%' OR
        experience_and_education LIKE '%бьюти%' OR experience_and_education LIKE '%красота%' OR
        experience_and_education LIKE '%косметик%' OR experience_and_education LIKE '%салон%' OR
        experience_and_education LIKE '%парикмахер%' OR experience_and_education LIKE '%ретейл%' OR
        experience_and_education LIKE '%ритейл%'
    )
    AND is_duplicate = 0
    LIMIT 20
""")
rows = cur.fetchall()

if rows:
    print(f"Найдено: {len(rows)}\n")
    for r in rows:
        dup = " (дубликат)" if r[6] else ""
        print(f"  ID={r[0]}, ФИО={r[1]}, Должность={r[3]}{dup}")
        exp_preview = str(r[5])[:200] if r[5] else ""
        if exp_preview:
            print(f"    Опыт: {exp_preview}")
        print()
else:
    print("❌ Не найдено HR в beauty/retail в Москве")

# General HR search with recruitment/KDP keywords
print("\n=== HR с опытом найма и КДП ===")
cur.execute("""
    SELECT row_id, fio, city_clean, desired_position, skills, experience_and_education
    FROM resumes 
    WHERE (
        desired_position LIKE '%HR%' OR 
        desired_position LIKE '%менеджер по персоналу%' OR
        desired_position LIKE '%специалист по персоналу%'
    )
    AND (
        skills LIKE '%найм%' OR skills LIKE '%рекрут%' OR skills LIKE '%КДП%' OR skills LIKE '%кадровое делопроизводство%' OR
        experience_and_education LIKE '%найм%' OR experience_and_education LIKE '%рекрут%' OR 
        experience_and_education LIKE '%КДП%' OR experience_and_education LIKE '%кадровое делопроизводство%'
    )
    AND city_clean = 'Москва'
    AND is_duplicate = 0
    LIMIT 10
""")
rows = cur.fetchall()
if rows:
    print(f"Найдено: {len(rows)}\n")
    for r in rows:
        print(f"  ID={r[0]}, ФИО={r[1]}, Должность={r[3]}")
        exp_preview = str(r[5])[:150] if r[5] else ""
        if exp_preview:
            print(f"    Опыт: {exp_preview}")
        print()

conn.close()
