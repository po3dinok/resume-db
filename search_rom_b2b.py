import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Head of Marketing / ROM / Директор по маркетингу (B2B) ===\n")

cur.execute("""
    SELECT row_id, fio, city_clean, desired_position, skills, experience_and_education, is_duplicate
    FROM resumes 
    WHERE (
        desired_position LIKE '%директор по маркетингу%' OR 
        desired_position LIKE '%head of marketing%' OR
        desired_position LIKE '%ром%' OR
        desired_position LIKE '%руководитель отдела маркетинга%' OR
        specialty LIKE '%директор по маркетингу%' OR
        specialty LIKE '%head of marketing%' OR
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
        exp_preview = str(r[5])[:150] if r[5] else ""
        if exp_preview:
            print(f"    Опыт: {exp_preview}")
        print()
else:
    print("❌ Не найдено")

# B2B marketing + industrial
print("\n=== B2B маркетинг + промышленное оборудование ===")
cur.execute("""
    SELECT row_id, fio, city_clean, desired_position, skills, experience_and_education
    FROM resumes 
    WHERE (
        skills LIKE '%B2B%' OR 
        experience_and_education LIKE '%B2B%' OR
        experience_and_education LIKE '%промышленн%оборудован%' OR
        experience_and_education LIKE '%промышленн%маркетинг%' OR
        desired_position LIKE '%B2B%маркетинг%'
    )
    AND (
        desired_position LIKE '%маркетинг%' OR
        desired_position LIKE '%marketing%' OR
        specialty LIKE '%маркетинг%'
    )
    AND is_duplicate = 0
    LIMIT 20
""")
rows = cur.fetchall()
if rows:
    print(f"Найдено: {len(rows)}\n")
    for r in rows:
        print(f"  ID={r[0]}, ФИО={r[1]}, Город={r[2]}, Должность={r[3]}")
        exp_preview = str(r[5])[:150] if r[5] else ""
        if exp_preview:
            print(f"    Опыт: {exp_preview}")
        print()

conn.close()
