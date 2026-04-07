import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Поиск забавных ФИО (Ещё глубже) ===\n")

categories = {
    "Фамилия = Имя (рифма)": [
        "%Светлов Свет%",
        "%Чернов Черн%",
        "%Белов Бел%",
        "%Краснов Красн%",
        "%Морозов Мороз%",
        "%Снегов Снег%",
        "%Жаров Жар%",
        "%Огнев Огон%",
        "%Водов Вод%",
        "%Земнов Зем%",
        "%Ветров Ветер%",
        "%Дождев Дожд%",
        "%Грозов Гроз%",
        "%Туманов Туман%",
    ],
    "Имя + Фамилия с юмором": [
        "%Любовь Любовь%",
        "%Вера Вера%",
        "%Надежда Надежда%",
        "%Слава Слава%",
        "%Мир Мир%",
        "%Богдан Богдан%",
        "%Захар Захар%",
        "%Данила Данил%",
        "%Тимофей Тимоф%",
        "%Савелий Савел%",
    ],
    "Необычные отчества": [
        "%Владиленович%",
        "%Владленович%",
        "%Даздрaper%",
        "%Нинель%",
        "%Октябринович%",
        "%Апрель%",
        "%Мартович%",
        "%Май%",
        "%Июнь%",
        "%Июль%",
        "%Декабрь%",
    ],
    "Короткие ФИО": [
        "%Я Я%",
        "%Ю Ю%",
        "%Э Э%",
    ],
    "Длинные ФИО": [
        "%ович %ович %ович%",
        "%евич %евич %евич%",
    ],
}

for cat, patterns in categories.items():
    print(f"--- {cat} ---")
    found_any = False
    for pattern in patterns:
        cur.execute("""
            SELECT fio FROM resumes 
            WHERE fio LIKE ? AND is_duplicate = 0 
            LIMIT 3
        """, (pattern,))
        rows = cur.fetchall()
        if rows:
            found_any = True
            for r in rows:
                print(f"  {r[0]}")
    if not found_any:
        print("  (Ничего не найдено)")
    print()

conn.close()
