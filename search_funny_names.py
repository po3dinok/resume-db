import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Поиск забавных ФИО ===\n")

# 1. Фамилия совпадает с именем (или похожа)
patterns = [
    ("%ов %ов%", "Фамилия-Имя (ов/ов)"),
    ("%ин %ин%", "Фамилия-Имя (ин/ин)"),
    ("%ев %ев%", "Фамилия-Имя (ев/ев)"),
    ("%ова %ова%", "Фамилия-Имя (ова/ова)"),
    ("%ова %ева%", "Фамилия-Имя (ова/ева)"),
]

for pattern, label in patterns:
    cur.execute("""
        SELECT fio FROM resumes WHERE fio LIKE ? AND is_duplicate = 0 LIMIT 5
    """, (pattern,))
    rows = cur.fetchall()
    if rows:
        print(f"--- {label} ---")
        for r in rows:
            print(f"  {r[0]}")
        print()

# 2. Имена, совпадающие с названиями животных/предметов
cur.execute("""
    SELECT fio FROM resumes 
    WHERE fio LIKE '%Кот%' OR fio LIKE '%Пес%' OR fio LIKE '%Волк%' OR 
          fio LIKE '%Лис%' OR fio LIKE '%Медвед%' OR fio LIKE '%Зайц%' OR
          fio LIKE '%Бык%' OR fio LIKE '%Кон%' OR fio LIKE '%Орл%' OR
          fio LIKE '%Гус%' OR fio LIKE '%Утк%' OR fio LIKE '%Попуга%'
    AND is_duplicate = 0 LIMIT 10
""")
rows = cur.fetchall()
if rows:
    print("--- Животные/Птицы ---")
    for r in rows:
        print(f"  {r[0]}")
    print()

conn.close()
