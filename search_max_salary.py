import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Топ-10 запросов по зарплате ===\n")

# Query to get top salaries, handling potential non-numeric values by casting
cur.execute("""
    SELECT fio, desired_position, desired_salary, city_clean 
    FROM resumes 
    WHERE desired_salary IS NOT NULL AND desired_salary != ''
    AND desired_salary GLOB '[0-9]*'
    ORDER BY CAST(desired_salary AS REAL) DESC
    LIMIT 10
""")
rows = cur.fetchall()

if rows:
    for r in rows:
        try:
            sal_num = float(r[2])
            formatted_sal = f"{sal_num:,.0f} руб."
        except:
            formatted_sal = r[2]
            
        print(f"  💰 {formatted_sal}")
        print(f"  👤 {r[0]}")
        print(f"  💼 {r[1]}")
        print(f"  📍 {r[3]}")
        print()
else:
    print("❌ Не найдено записей с зарплатой")

conn.close()
