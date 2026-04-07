import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

keywords = [
    'наличие автомобиля',
    'свой автомобиль',
    'личный автомобиль',
    'есть автомобиль',
    'собственный автомобиль',
    'наличие машины',
    'своя машина',
    'личный автомобиль',
    'автомобиль в собственности',
]

print("=== Поиск упоминаний автомобиля в резюме ===\n")

for kw in keywords:
    cur.execute("""
        SELECT COUNT(DISTINCT row_id) FROM resumes 
        WHERE skills LIKE ? OR additional_info LIKE ? OR specialty LIKE ? OR experience_and_education LIKE ?
    """, (f'%{kw}%', f'%{kw}%', f'%{kw}%', f'%{kw}%'))
    count = cur.fetchone()[0]
    print(f"  '{kw}': {count:,}")

# Combined search
cur.execute("""
    SELECT COUNT(DISTINCT row_id) FROM resumes 
    WHERE skills LIKE '%автомобиль%' OR additional_info LIKE '%автомобиль%' OR specialty LIKE '%автомобиль%' OR experience_and_education LIKE '%автомобиль%'
""")
total_auto = cur.fetchone()[0]
print(f"\n🚗 Всего с упоминанием 'автомобиль': {total_auto:,}")

conn.close()
