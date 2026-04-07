import sqlite3
import os
import shutil
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r"D:\DevScripts\ResumeDB\resume.db"
PDF_FOLDER = r"D:\ИНВЕНИУМ+\База резюме"
OUTPUT_FOLDER = r""./output"

# Обновленные запросы с расширенными ключевыми словами для лучшего покрытия
requests = [
    # Инженер строительного контроля
    ("Инженер строительного контроля", "Уфа", 100, ["инженер строительного контроля", "главный инженер", "инженер технадзора", "технадзор", "строительный контроль"]),
    ("Инженер строительного контроля", "Ростов-на-Дону", 100, ["инженер строительного контроля", "главный инженер", "инженер технадзора", "технадзор", "строительный контроль"]),
    ("Инженер строительного контроля", "Хабаровск", 100, ["инженер строительного контроля", "главный инженер", "инженер технадзора", "технадзор", "строительный контроль"]),
    ("Инженер строительного контроля", "Дмитров", 50, ["инженер строительного контроля", "главный инженер", "инженер технадзора", "технадзор", "строительный контроль"]),
    ("Инженер строительного контроля", "Зеленоград", 50, ["инженер строительного контроля", "главный инженер", "инженер технадзора", "технадзор", "строительный контроль"]),
    
    # Руководитель проекта
    ("Руководитель проекта", "Курск", 50, ["руководитель проекта", "project manager", "ГИП", "главный инженер проекта", "руководитель строительства"]),
    ("Руководитель проекта", "Смоленск", 50, ["руководитель проекта", "project manager", "ГИП", "главный инженер проекта", "руководитель строительства"]),
    ("Руководитель проекта", "Брянск", 50, ["руководитель проекта", "project manager", "ГИП", "главный инженер проекта", "руководитель строительства"]),
    ("Руководитель проекта", "Вологда", 50, ["руководитель проекта", "project manager", "ГИП", "главный инженер проекта", "руководитель строительства"]),
    
    # Менеджер по продажам
    ("Менеджер по продажам", "Москва", 200, ["менеджер по продажам", "sales manager", "торговый представитель", "менеджер по работе с клиентами", "account manager"]),
    
    # Маркетолог
    ("Маркетолог", "Москва", 100, ["маркетолог", "маркетинг", "digital marketing", "brand manager", "product manager", "интернет-маркетолог"]),
    
    # Директор по маркетингу
    ("Директор по маркетингу", "Москва", 100, ["директор по маркетингу", "marketing director", "CMO", "руководитель отдела маркетинга", "директор маркетинга"]),
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

total_copied = 0

for title, city, limit, keywords in requests:
    # Create folder
    folder_name = f"{title} - {city}"
    folder_path = os.path.join(OUTPUT_FOLDER, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    # Build query
    conditions = []
    params = [f'%{city}%']
    for kw in keywords:
        conditions.append("(desired_position LIKE ? OR experience_and_education LIKE ?)")
        params.extend([f'%{kw}%', f'%{kw}%'])
    
    query = f"SELECT row_id, fio, desired_position, city FROM resumes WHERE city LIKE ? AND ({' OR '.join(conditions)}) LIMIT {limit}"
    
    try:
        cur.execute(query, params)
        rows = cur.fetchall()
    except Exception as e:
        print(f"Error querying {title} in {city}: {e}")
        continue

    copied = 0
    for row_id, fio, pos, rcity in rows:
        # Find PDF file
        fio_clean = ' '.join(fio.split())
        try:
            matching_pdfs = [f for f in os.listdir(PDF_FOLDER) if f.lower().startswith(fio_clean.lower()) and f.lower().endswith('.pdf')]
        except FileNotFoundError:
            continue
        
        for pdf_file in matching_pdfs:
            src = os.path.join(PDF_FOLDER, pdf_file)
            dst = os.path.join(folder_path, pdf_file)
            if not os.path.exists(dst):
                try:
                    shutil.copy2(src, dst)
                    copied += 1
                    total_copied += 1
                except Exception as e:
                    pass # Ignore copy errors
            break # Only copy first match per candidate

    print(f"{'✅' if copied >= limit else '⚠️'} {folder_name}: {copied} резюме (нужно {limit})")

conn.close()
print(f"\nВсего скопировано: {total_copied} резюме в {OUTPUT_FOLDER}")
