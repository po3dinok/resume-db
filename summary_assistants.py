import sqlite3
import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db', timeout=10)
cur = conn.cursor()

# Get IDs
cur.execute("""
    SELECT row_id FROM resumes 
    WHERE schedule LIKE '%удален%'
    AND desired_position LIKE '%ассистент%'
    AND is_duplicate = 0
""")
ids = [row[0] for row in cur.fetchall()]

print(f"📊 Сводка по {len(ids)} бизнес-ассистентам (удалённо)\n")

# Get details in one query
placeholders = ','.join('?' for _ in ids)
query = f"""
    SELECT row_id, desired_salary, experience, education_category, city_clean, skills, additional_info
    FROM resumes 
    WHERE row_id IN ({placeholders})
"""
rows = cur.execute(query, ids).fetchall()

# Analysis
salaries = []
cities = {}
experiences = {}
english_count = 0
skills_count = {}

for r in rows:
    # City
    city = r[4] if r[4] else "Не указан"
    cities[city] = cities.get(city, 0) + 1
    
    # Experience
    exp = r[2] if r[2] else "Не указан"
    experiences[exp] = experiences.get(exp, 0) + 1
    
    # Salary
    sal_text = r[1]
    if sal_text:
        # Try to extract number
        nums = re.findall(r'(\d+)', str(sal_text))
        if nums:
            salaries.append(int(nums[0]))
            
    # Skills
    skills = str(r[5]).lower()
    if 'английский' in skills or 'english' in skills:
        english_count += 1
        
    # Common skills
    for kw in ['1с', 'crm', 'bitrix', 'excel', 'word', 'google', 'trello', 'notion', 'jira']:
        if kw in skills:
            skills_count[kw] = skills_count.get(kw, 0) + 1

# Print results
print("📍 География:")
sorted_cities = sorted(cities.items(), key=lambda x: x[1], reverse=True)
for city, count in sorted_cities[:10]:
    print(f"  {city}: {count}")

print("\n💰 Желаемая зарплата:")
if salaries:
    print(f"  Мин: {min(salaries):,} ₽")
    print(f"  Макс: {max(salaries):,} ₽")
    print(f"  Среднее: {sum(salaries)//len(salaries):,} ₽")
    print(f"  Медиана: {sorted(salaries)[len(salaries)//2]:,} ₽")
else:
    print("  Нет данных")

print("\n🎓 Опыт работы:")
for exp, count in sorted(experiences.items(), key=lambda x: x[1], reverse=True):
    print(f"  {exp}: {count}")

print(f"\n🌍 Английский язык: {english_count} ({english_count/len(ids)*100:.0f}%)")

print("\n💻 Навыки:")
for skill, count in sorted(skills_count.items(), key=lambda x: x[1], reverse=True):
    print(f"  {skill.upper()}: {count}")

conn.close()
