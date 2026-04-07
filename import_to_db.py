import pandas as pd
import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

EXCEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'База резюме 20+.xlsx')
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resume.db')

COLUMN_MAP = {
    'ФИО': 'fio',
    'Статус': 'status',
    'Пол': 'gender',
    'Возраст': 'age',
    'Дата рождения': 'birth_date',
    'Населенный пункт': 'city',
    'Гражданство': 'citizenship',
    'Готовность к переезду': 'relocation',
    'Готовность к командировкам': 'business_trips',
    'Желаемая должность': 'desired_position',
    'Специальность': 'specialty',
    'Желаемый оклад': 'desired_salary',
    'Занятость': 'employment',
    'График работы': 'schedule',
    'Желательное время в пути до работы': 'commute_time',
    'Стаж': 'experience',
    'Опыт работы и образование': 'experience_and_education',
    'Категория образования': 'education_category',
    'Навыки': 'skills',
    'Права категории': 'license_category',
    'Дополнительная информация': 'additional_info',
    'История общения с кандидатом': 'communication_history',
    'Телефон': 'phone',
    'Почта': 'email',
    'WhatsApp': 'whatsapp',
    'Telegram': 'telegram',
    'Яндекс Карты': 'yandex_maps',
    'Дата обновления резюме': 'resume_update_date',
    'НРС': 'nrs',
    'НОПРИЗ': 'nopriz',
    'НАКС': 'naks',
    'ВИК': 'vik',
    'ОТТБ': 'ottb',
    'ОВ': 'ov',
    'МК': 'mk',
    'ВК': 'vk',
    'ЭЛ': 'el',
    'СС': 'ss',
    'id': 'resume_id',
}

print('Чтение Excel...')
df = pd.read_excel(EXCEL_PATH)
df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]
df = df.rename(columns=COLUMN_MAP)
df = df.fillna('')
for col in df.columns:
    df[col] = df[col].astype(str).str.strip()

# Нормализуем числовые поля
df['age'] = pd.to_numeric(df['age'], errors='coerce')
df['desired_salary'] = pd.to_numeric(df['desired_salary'].astype(str).str.replace(r'[^\d]', '', regex=True), errors='coerce')

# Уникальный row_id
df.insert(0, 'row_id', range(1, len(df) + 1))

print(f'Записей: {len(df)}')
print('Создание SQLite базы...')

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)

# Создаём таблицу
col_defs = ['"row_id" INTEGER PRIMARY KEY']
for col in df.columns:
    if col == 'row_id':
        continue
    if col in ('age', 'desired_salary'):
        col_defs.append(f'"{col}" REAL')
    else:
        col_defs.append(f'"{col}" TEXT')

create_sql = f'CREATE TABLE resumes ({", ".join(col_defs)})'
conn.execute(create_sql)

df.to_sql('resumes', conn, if_exists='replace', index=False)

# Индексы
indexes = [
    'CREATE INDEX idx_fio ON resumes("fio")',
    'CREATE INDEX idx_desired_position ON resumes("desired_position")',
    'CREATE INDEX idx_city ON resumes("city")',
    'CREATE INDEX idx_gender ON resumes("gender")',
    'CREATE INDEX idx_experience ON resumes("experience")',
    'CREATE INDEX idx_education ON resumes("education_category")',
    'CREATE INDEX idx_citizenship ON resumes("citizenship")',
    'CREATE INDEX idx_business_trips ON resumes("business_trips")',
    'CREATE INDEX idx_employment ON resumes("employment")',
    'CREATE INDEX idx_schedule ON resumes("schedule")',
    'CREATE INDEX idx_commute_time ON resumes("commute_time")',
    'CREATE INDEX idx_license ON resumes("license_category")',
    'CREATE INDEX idx_nrs ON resumes("nrs")',
    'CREATE INDEX idx_naks ON resumes("naks")',
    'CREATE INDEX idx_nopriz ON resumes("nopriz")',
    'CREATE INDEX idx_vik ON resumes("vik")',
    'CREATE INDEX idx_ottb ON resumes("ottb")',
    'CREATE INDEX idx_ov ON resumes("ov")',
    'CREATE INDEX idx_mk ON resumes("mk")',
    'CREATE INDEX idx_vk ON resumes("vk")',
    'CREATE INDEX idx_el ON resumes("el")',
    'CREATE INDEX idx_ss ON resumes("ss")',
    'CREATE INDEX idx_age ON resumes("age")',
    'CREATE INDEX idx_salary ON resumes("desired_salary")',
    'CREATE INDEX idx_resume_id ON resumes("resume_id")',
    'CREATE INDEX idx_phone ON resumes("phone")',
    'CREATE INDEX idx_email ON resumes("email")',
    'CREATE INDEX idx_skills ON resumes("skills")',
    'CREATE INDEX idx_relocation ON resumes("relocation")',
]

for idx_sql in indexes:
    conn.execute(idx_sql)

conn.commit()

# Проверка
count = conn.execute('SELECT COUNT(*) FROM resumes').fetchone()[0]
print(f'Готово! {count} записей в базе {DB_PATH}')

conn.close()
