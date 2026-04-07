import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Поиск забавных ФИО (расширенный) ===\n")

# 1. Имя-Отчество рифмуются
cur.execute("""
    SELECT fio FROM resumes 
    WHERE fio LIKE '%ович %ович%' OR fio LIKE '%евич %евич%' OR 
          fio LIKE '%овна %овна%' OR fio LIKE '%евна %евна%' OR
          fio LIKE '%ич %ич%' OR fio LIKE '%на %на%'
    AND is_duplicate = 0 LIMIT 10
""")
rows = cur.fetchall()
if rows:
    print("--- Рифмующиеся отчества ---")
    for r in rows:
        print(f"  {r[0]}")
    print()

# 2. Фамилия = Имя (полное совпадение части)
cur.execute("""
    SELECT fio FROM resumes 
    WHERE fio LIKE '%Петров Петр%' OR fio LIKE '%Иванов Иван%' OR 
          fio LIKE '%Сидоров Сидор%' OR fio LIKE '%Кузнецов Кузнец%' OR
          fio LIKE '%Попов Поп%' OR fio LIKE '%Смирнов Смирн%'
    AND is_duplicate = 0 LIMIT 10
""")
rows = cur.fetchall()
if rows:
    print("--- Фамилия = Имя (классика) ---")
    for r in rows:
        print(f"  {r[0]}")
    print()

# 3. Необычные имена
cur.execute("""
    SELECT fio FROM resumes 
    WHERE fio LIKE '%Ангел%' OR fio LIKE '%Демон%' OR fio LIKE '%Дьявол%' OR 
          fio LIKE '%Рай%' OR fio LIKE '%Ад%' OR fio LIKE '%Бог%' OR
          fio LIKE '%Сатан%' OR fio LIKE '%Люцифер%' OR fio LIKE '%Иисус%' OR
          fio LIKE '%Будда%' OR fio LIKE '%Иуда%' OR fio LIKE '%Царь%' OR
          fio LIKE '%Князь%' OR fio LIKE '%Принц%' OR fio LIKE '%Король%'
    AND is_duplicate = 0 LIMIT 10
""")
rows = cur.fetchall()
if rows:
    print("--- Королевские/Божественные имена ---")
    for r in rows:
        print(f"  {r[0]}")
    print()

# 4. Фамилия-Имя-Отчество совпадают по звучанию
cur.execute("""
    SELECT fio FROM resumes 
    WHERE fio LIKE '%Светлов Свет%' OR fio LIKE '%Чернов Черн%' OR 
          fio LIKE '%Белов Бел%' OR fio LIKE '%Краснов Красн%' OR
          fio LIKE '%Молодов Молод%' OR fio LIKE '%Старов Стар%' OR
          fio LIKE '%Тихов Тих%' OR fio LIKE '%Громов Гром%'
    AND is_duplicate = 0 LIMIT 10
""")
rows = cur.fetchall()
if rows:
    print("--- Говорящие фамилии ---")
    for r in rows:
        print(f"  {r[0]}")
    print()

# 5. Имя-Фамилия с юмором
cur.execute("""
    SELECT fio FROM resumes 
    WHERE fio LIKE '%Любовь%' OR fio LIKE '%Надежда%' OR fio LIKE '%Вера%' OR
          fio LIKE '%Счастье%' OR fio LIKE '%Радость%' OR fio LIKE '%Удача%' OR
          fio LIKE '%Забава%' OR fio LIKE '%Смех%' OR fio LIKE '%Весел%'
    AND is_duplicate = 0 LIMIT 10
""")
rows = cur.fetchall()
if rows:
    print("--- Имена-эмоции ---")
    for r in rows:
        print(f"  {r[0]}")
    print()

conn.close()
