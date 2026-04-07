#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLI для поиска по базе резюме.
Используется AI-ассистентом через bash-команды.

Команды:
    python cli.py найти "инженер ПТО"
    python cli.py найти "сварщик" --город Москва --накс yes
    python cli.py найти "электрик" --зарплата-от 80000 --лимит 10
    python cli.py детально <id>
    python cli.py стата
    python cli.py файлы "Иванов Иван"
    python cli.py найти "прораб" --файлы
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import argparse
import sqlite3
import os
import glob
import re
import csv

DB_PATH = os.path.join(r'D:\DevScripts\ResumeDB', 'resume.db')
SEARCH_DIRS = [
    r'D:\ИНВЕНИУМ+\База резюме',
    r'D:\DevScripts\Docs',
    r'D:\DevScripts\Инвениум 1.6',
    r'D:\DevScripts\Инвениум 1.5',
    r'D:\DevScripts',
]

# Can be overridden via --resume-dir flag
RESUME_DIR = None


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def dr(row):
    return dict(zip(row.keys(), row))


def fmt_salary(val):
    if not val or val == 'None':
        return ''
    try:
        return f'{int(float(val)):,}'.replace(',', ' ') + ' rub'
    except:
        return str(val)


def trunc(val, n=120):
    if not val or val == 'None':
        return ''
    t = str(val).replace('\n', ' ').strip()
    return t[:n] + '...' if len(t) > n else t


def has_cert(val):
    return val and val != 'None' and 'есть' in str(val).lower()


def find_resume_files(fio):
    if not fio or fio == 'None':
        return []
    parts = fio.strip().split()
    if not parts:
        return []
    last_name = parts[0].lower()

    results = []
    for search_dir in SEARCH_DIRS:
        if not os.path.isdir(search_dir):
            continue
        for root, dirs, files in os.walk(search_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            for f in files:
                f_lower = f.lower()
                if last_name in f_lower:
                    score = 1
                    if len(parts) > 1 and parts[1].lower() in f_lower:
                        score += 1
                    if len(parts) > 2 and parts[2].lower() in f_lower:
                        score += 1
                    full_path = os.path.join(root, f)
                    results.append((score, full_path))

    results.sort(key=lambda x: -x[0])
    return results[:5]


def normalize_phone(phone_str):
    if not phone_str or phone_str == 'None':
        return ''
    digits = ''.join(c for c in str(phone_str) if c.isdigit())
    if len(digits) == 11 and digits[0] == '7':
        return digits
    elif len(digits) == 11 and digits[0] == '8':
        return '7' + digits[1:]
    elif len(digits) == 10:
        return '7' + digits
    return digits


def search_by_phone(phone_query):
    db = get_db()
    query_digits = ''.join(c for c in phone_query if c.isdigit())
    if not query_digits:
        db.close()
        return []

    rows = db.execute('SELECT row_id, fio, desired_position, city, phone, email FROM resumes WHERE phone IS NOT NULL').fetchall()
    results = []
    for row in rows:
        d = dr(row)
        digits = normalize_phone(d.get('phone'))
        if query_digits in digits:
            results.append(d)
    db.close()
    return results


def build_query(args, db=None):
    conditions = []
    params = []

    if args.phone:
        phone_digits = normalize_phone(args.phone)
        if phone_digits and db:
            rows = db.execute("SELECT row_id, phone, email, whatsapp, telegram FROM resumes WHERE phone IS NOT NULL OR email IS NOT NULL OR whatsapp IS NOT NULL OR telegram IS NOT NULL").fetchall()
            matching_ids = []
            for r in rows:
                for col_name in ['phone', 'email', 'whatsapp', 'telegram']:
                    val = r[col_name]
                    if val and val != 'None':
                        digits = normalize_phone(val)
                        if phone_digits in digits:
                            matching_ids.append(r['row_id'])
                            break
            if matching_ids:
                placeholders = ','.join('?' for _ in matching_ids)
                conditions.append(f'r.row_id IN ({placeholders})')
                params.extend(matching_ids)
            else:
                conditions.append('r.row_id = -1')

    if args.query:
        # Use FTS5 for full-text search
        import re
        keywords = [w.strip() for w in re.split(r'[\s,;]+', args.query) if len(w.strip()) > 1]
        if keywords:
            # Escape FTS5 special characters
            escaped = [k.replace('"', '""') for k in keywords]
            fts_query = ' AND '.join([f'"{e}"' for e in escaped])
            try:
                fts_results = db.execute("""
                    SELECT rowid FROM resume_fts WHERE resume_fts MATCH ?
                """, (fts_query,)).fetchall()
            except sqlite3.OperationalError:
                fts_results = []
            if fts_results:
                fts_ids = [r[0] for r in fts_results]
                placeholders = ','.join('?' for _ in fts_ids)
                conditions.append(f'r.rowid IN ({placeholders})')
                params.extend(fts_ids)
                args._fts_query = fts_query
            else:
                # Fallback to LIKE
                like = f'%{args.query}%'
                conditions.append(
                    "(r.fio LIKE ? OR r.desired_position LIKE ? "
                    "OR r.city LIKE ? OR r.skills LIKE ? "
                    "OR r.specialty LIKE ? "
                    "OR r.email LIKE ? "
                    "OR r.experience_and_education LIKE ? "
                    "OR r.additional_info LIKE ?)"
                )
                params.extend([like] * 8)
        else:
            like = f'%{args.query}%'
            conditions.append(
                "(r.fio LIKE ? OR r.desired_position LIKE ? "
                "OR r.city LIKE ? OR r.skills LIKE ? "
                "OR r.specialty LIKE ? "
                "OR r.email LIKE ? "
                "OR r.experience_and_education LIKE ? "
                "OR r.additional_info LIKE ?)"
            )
            params.extend([like] * 8)

    if args.city:
        conditions.append("(r.city_clean LIKE ? OR r.city LIKE ?)")
        params.extend([f'%{args.city}%', f'%{args.city}%'])

    if args.metro:
        conditions.append("r.metro LIKE ?")
        params.append(f'%{args.metro}%')

    if args.gender:
        conditions.append("r.gender = ?")
        params.append(args.gender)

    if args.age_from:
        conditions.append("r.age >= ?")
        params.append(float(args.age_from))
    if args.age_to:
        conditions.append("r.age <= ?")
        params.append(float(args.age_to))

    if args.experience:
        conditions.append("r.experience = ?")
        params.append(args.experience)

    if args.exp_from:
        conditions.append("r.experience_months >= ?")
        params.append(int(args.exp_from))

    if args.education:
        conditions.append("r.education_category = ?")
        params.append(args.education)

    if args.salary_from:
        conditions.append("r.desired_salary >= ?")
        params.append(float(args.salary_from))
    if args.salary_to:
        conditions.append("r.desired_salary <= ?")
        params.append(float(args.salary_to))

    if args.employment:
        conditions.append("r.employment LIKE ?")
        params.append(f'%{args.employment}%')

    if args.schedule:
        conditions.append("r.schedule LIKE ?")
        params.append(f'%{args.schedule}%')

    if args.business_trips:
        conditions.append("r.business_trips = 'Готов/а'")

    if args.relocation:
        conditions.append("r.relocation LIKE '%готов к переезду%'")

    if args.license:
        conditions.append("r.license_category = ?")
        params.append(args.license)

    if args.skills:
        conditions.append("r.skills LIKE ?")
        params.append(f'%{args.skills}%')

    if args.skill:
        conditions.append("r.skills_normalized LIKE ?")
        params.append(f'%{args.skill}%')

    if args.company:
        conditions.append("r.companies LIKE ?")
        params.append(f'%{args.company}%')

    if args.valid_contacts:
        conditions.append("r.phone_valid = 1 AND r.email_valid = 1")

    certs_map = {
        'nrs': 'nrs', 'naks': 'naks', 'nopriz': 'nopriz',
        'vik': 'vik', 'ottb': 'ottb', 'ov': 'ov',
        'mk': 'mk', 'vk': 'vk', 'el': 'el', 'ss': 'ss'
    }
    for cert_key, col in certs_map.items():
        val = getattr(args, cert_key, None)
        if val == 'yes':
            conditions.append(f"(r.{col} LIKE '%Есть%' OR r.{col} LIKE '%есть%')")
        elif val == 'no':
            conditions.append(f"(r.{col} LIKE '%Нет%' OR r.{col} LIKE '%нет%')")

    where = ' AND '.join(conditions) if conditions else '1=1'
    return where, params


def cmd_find(args):
    db = get_db()
    where, params = build_query(args, db=db)

    # Use 'r.' prefix for all column references when using FTS5 JOIN
    if args.query and hasattr(args, '_fts_query'):
        where = where.replace('rowid IN resume_fts', 'r.rowid IN resume_fts')
        where = where.replace('r.r.rowid', 'r.rowid')

    sort = 'r.desired_salary DESC' if args.sort == 'salary' else \
           'r.age ASC' if args.sort == 'age' else \
           'r.experience DESC' if args.sort == 'exp' else \
           'r.row_id DESC'

    # FTS5 relevance ranking
    if args.query and hasattr(args, '_fts_query') and not args.sort:
        # Get ordered IDs from FTS5 (already sorted by relevance)
        fts_ids = [r[0] for r in db.execute(
            "SELECT rowid FROM resume_fts WHERE resume_fts MATCH ?",
            (args._fts_query,)
        ).fetchall()]
        if fts_ids:
            sort = f"CASE r.rowid " + ' '.join(f'WHEN {rid} THEN {i}' for i, rid in enumerate(fts_ids)) + f" ELSE {len(fts_ids)} END"

    count_sql = f'SELECT COUNT(*) FROM resumes r WHERE {where}'
    total = db.execute(count_sql, params).fetchone()[0]

    if total == 0:
        print(f'\nNOT FOUND: 0 candidates')
        if args.query:
            print(f'Query: "{args.query}"')
        print()
        db.close()
        return

    limit = args.limit or 20
    cols = [
        'row_id', 'fio', 'desired_position', 'city', 'desired_salary',
        'experience', 'gender', 'age', 'education_category',
        'nrs', 'naks', 'nopriz', 'vik', 'ottb', 'ov', 'mk', 'vk', 'el',
        'license_category', 'business_trips', 'phone', 'email',
        'resume_update_date', 'citizenship', 'skills'
    ]
    select_cols = ', '.join(f'r."{c}"' for c in cols)
    rows = db.execute(
        f'SELECT {select_cols} FROM resumes r WHERE {where} ORDER BY {sort} LIMIT ?',
        params + [limit]
    ).fetchall()

    print(f'\nFOUND: {total} candidates (showing {len(rows)})')
    if args.query:
        print(f'Query: "{args.query}"')
    print('=' * 80)

    for row in rows:
        d = dr(row)
        certs = []
        for c, name in [('nrs','НРС'),('naks','НАКС'),('nopriz','НОПРИЗ'),('vik','ВИК'),
                         ('ottb','ОТТБ'),('ov','ОВ'),('mk','МК'),('vk','ВК'),('el','ЭЛ')]:
            if has_cert(d.get(c)):
                certs.append(name)

        print(f'\nID: {d["row_id"]}')
        print(f'  Name:     {d["fio"] or "N/A"}')
        print(f'  Position: {d["desired_position"] or "N/A"}')
        print(f'  City:     {d["city"] or "N/A"}')
        sal = fmt_salary(d.get('desired_salary'))
        if sal:
            print(f'  Salary:   {sal}')
        print(f'  Exp:      {d["experience"] or "N/A"}')
        if d.get('age') and d['age'] != 'None':
            print(f'  Age:      {d["age"]}')
        if d.get('education_category') and d['education_category'] != 'не указано':
            print(f'  Edu:      {d["education_category"]}')
        if certs:
            print(f'  Certs:    {", ".join(certs)}')
        if d.get('phone') and d['phone'] != 'None':
            print(f'  Phone:    {d["phone"].split(chr(10))[0]}')
        if d.get('email') and d['email'] != 'None':
            print(f'  Email:    {d["email"]}')

        if args.files:
            files = find_resume_files(d.get('fio'))
            if files:
                for score, path in files:
                    print(f'  File:     {path}')

    print(f'\n{"=" * 80}')
    print(f'Use "python cli.py детально <ID>" for full details')
    print()

    db.close()


def cmd_detail(args):
    db = get_db()
    row = db.execute('SELECT * FROM resumes WHERE row_id = ?', (args.id,)).fetchone()
    if not row:
        print(f'\nNOT FOUND: candidate with ID {args.id}')
        db.close()
        return

    d = dr(row)

    print(f'\n{"=" * 80}')
    print(f'ID: {d["row_id"]}')
    print(f'Name:     {d["fio"] or "N/A"}')
    print(f'Position: {d["desired_position"] or "N/A"}')
    sal = fmt_salary(d.get('desired_salary'))
    if sal:
        print(f'Salary:   {sal}')
    print(f'{"=" * 80}')

    print(f'\n--- Basic Info ---')
    print(f'  City:           {d.get("city") or "N/A"}')
    if d.get('age') and d['age'] != 'None':
        print(f'  Age:            {d["age"]}')
    print(f'  Gender:         {d.get("gender") or "N/A"}')
    print(f'  Citizenship:    {d.get("citizenship") or "N/A"}')
    print(f'  Birth date:     {d.get("birth_date") or "N/A"}')
    print(f'  Experience:     {d.get("experience") or "N/A"}')
    print(f'  Education:      {d.get("education_category") or "N/A"}')
    print(f'  Employment:     {d.get("employment") or "N/A"}')
    print(f'  Schedule:       {d.get("schedule") or "N/A"}')
    print(f'  Relocation:     {d.get("relocation") or "N/A"}')
    print(f'  Business trips: {d.get("business_trips") or "N/A"}')
    print(f'  Commute time:   {d.get("commute_time") or "N/A"}')
    if d.get('license_category') and d['license_category'] != 'Нет':
        print(f'  License:        Category {d["license_category"]}')
    print(f'  Updated:        {d.get("resume_update_date") or "N/A"}')

    certs = []
    for c, name in [('nrs','НРС'),('naks','НАКС'),('nopriz','НОПРИЗ'),('vik','ВИК'),
                     ('ottb','ОТТБ'),('ov','ОВ'),('mk','МК'),('vk','ВК'),('el','ЭЛ'),('ss','СС')]:
        if has_cert(d.get(c)):
            certs.append(name)
    if certs:
        print(f'  Certificates:   {", ".join(certs)}')

    print(f'\n--- Contacts ---')
    if d.get('phone') and d['phone'] != 'None':
        print(f'  Phone:    {d["phone"]}')
    if d.get('email') and d['email'] != 'None':
        print(f'  Email:    {d["email"]}')
    if d.get('whatsapp') and d['whatsapp'] != 'None':
        print(f'  WhatsApp: {d["whatsapp"].split(chr(10))[0]}')
    if d.get('telegram') and d['telegram'] != 'None':
        print(f'  Telegram: {d["telegram"].split(chr(10))[0]}')
    if d.get('yandex_maps') and d['yandex_maps'] != 'None':
        print(f'  Maps:     {d["yandex_maps"]}')

    if d.get('specialty') and d['specialty'] != 'None':
        print(f'\n--- Specialty ---')
        print(f'  {d["specialty"]}')

    if d.get('skills') and d['skills'] != 'None':
        print(f'\n--- Skills ---')
        print(f'  {trunc(d["skills"], 300)}')

    if d.get('experience_and_education') and d['experience_and_education'] != 'None':
        print(f'\n--- Experience & Education ---')
        print(f'  {trunc(d["experience_and_education"], 500)}')

    if d.get('additional_info') and d['additional_info'] != 'None':
        print(f'\n--- Additional Info ---')
        print(f'  {trunc(d["additional_info"], 500)}')

    if d.get('communication_history') and d['communication_history'] != 'None':
        print(f'\n--- Communication History ---')
        print(f'  {trunc(d["communication_history"], 500)}')

    files = find_resume_files(d.get('fio'))
    if files and getattr(args, 'files', False):
        print(f'\n--- Resume Files ---')
        for score, path in files:
            print(f'  {path}')

    print(f'\n{"=" * 80}')
    print()

    db.close()


def cmd_stats(args):
    db = get_db()
    total = db.execute('SELECT COUNT(*) FROM resumes').fetchone()[0]

    print(f'\n=== DATABASE STATS: {total:,} resumes ===\n')

    print('Gender:')
    for r in db.execute('SELECT gender, COUNT(*) as cnt FROM resumes GROUP BY gender ORDER BY cnt DESC'):
        pct = r[1] / total * 100
        print(f'  {r[0]:20s} {r[1]:>7,}  ({pct:.1f}%)')

    print('\nExperience:')
    for r in db.execute('SELECT experience, COUNT(*) as cnt FROM resumes GROUP BY experience ORDER BY cnt DESC'):
        pct = r[1] / total * 100
        print(f'  {(r[0] or "N/A"):20s} {r[1]:>7,}  ({pct:.1f}%)')

    print('\nEducation:')
    for r in db.execute('SELECT education_category, COUNT(*) as cnt FROM resumes GROUP BY education_category ORDER BY cnt DESC LIMIT 8'):
        print(f'  {(r[0] or "N/A"):25s} {r[1]:>7,}')

    print('\nTop 15 Cities:')
    for r in db.execute("SELECT city, COUNT(*) as cnt FROM resumes WHERE city != '' GROUP BY city ORDER BY cnt DESC LIMIT 15"):
        print(f'  {r[0]:40s} {r[1]:>7,}')

    print('\nCertificates:')
    for col, name in [('nrs','НРС'),('naks','НАКС'),('nopriz','НОПРИЗ'),('vik','ВИК'),
                       ('ottb','ОТТБ'),('ov','ОВ'),('mk','МК'),('vk','ВК'),('el','ЭЛ'),('ss','СС')]:
        cnt = db.execute(f"SELECT COUNT(*) FROM resumes WHERE {col} LIKE '%Есть%' OR {col} LIKE '%есть%'").fetchone()[0]
        pct = cnt / total * 100
        print(f'  {name:10s} {cnt:>6,}  ({pct:.1f}%)')

    salary = db.execute('''
        SELECT MIN(desired_salary), MAX(desired_salary), AVG(desired_salary)
        FROM resumes WHERE desired_salary IS NOT NULL
    ''').fetchone()
    if salary[0]:
        print(f'\nSalary:')
        print(f'  Min:     {fmt_salary(salary[0])}')
        print(f'  Max:     {fmt_salary(salary[1])}')
        print(f'  Average: {fmt_salary(salary[2])}')

    print()
    db.close()


def cmd_files(args):
    fio = args.name
    files = find_resume_files(fio)
    if not files:
        print(f'\nNo resume files found for "{fio}"')
        print(f'Searched in:')
        for d in SEARCH_DIRS:
            if os.path.isdir(d):
                print(f'  {d}')
        print()
        return

    print(f'\nResume files for "{fio}":')
    for score, path in files:
        size = os.path.getsize(path)
        print(f'  {path} ({size:,} bytes)')
    print()



def cmd_export(args):
    """Экспорт результатов поиска в CSV."""
    # Set defaults for missing args
    for attr in ['phone', 'city', 'metro', 'gender', 'age_from', 'age_to',
                 'experience', 'exp_from', 'education', 'salary_from', 'salary_to',
                 'employment', 'schedule', 'business_trips', 'relocation',
                 'license', 'skills', 'nrs', 'naks', 'nopriz', 'vik', 'ottb',
                 'ov', 'mk', 'vk', 'el', 'ss']:
        if not hasattr(args, attr):
            setattr(args, attr, None)

    db = get_db()
    where, params = build_query(args, db=db)

    if args.query and hasattr(args, '_fts_query'):
        where = where.replace('rowid IN resume_fts', 'r.rowid IN resume_fts')
        where = where.replace('r.r.rowid', 'r.rowid')

    cols = [
        'row_id', 'fio', 'desired_position', 'city', 'desired_salary',
        'experience', 'gender', 'age', 'education_category',
        'nrs', 'naks', 'nopriz', 'vik', 'ottb', 'ov', 'mk', 'vk', 'el', 'ss',
        'license_category', 'business_trips', 'relocation',
        'phone', 'email', 'telegram', 'whatsapp',
        'skills', 'specialty', 'experience_and_education',
        'additional_info', 'resume_update_date', 'citizenship',
        'city_clean', 'metro', 'experience_months'
    ]
    select_cols = ', '.join(f'r."{c}"' for c in cols)

    # FTS5 relevance ordering
    sort = 'r.row_id DESC'
    if args.query and hasattr(args, '_fts_query'):
        fts_ids = [r[0] for r in db.execute(
            "SELECT rowid FROM resume_fts WHERE resume_fts MATCH ?",
            (args._fts_query,)
        ).fetchall()]
        if fts_ids:
            sort = "CASE r.rowid " + ' '.join(f'WHEN {rid} THEN {i}' for i, rid in enumerate(fts_ids)) + f" ELSE {len(fts_ids)} END"

    limit = args.limit or 1000
    rows = db.execute(
        f'SELECT {select_cols} FROM resumes r WHERE {where} ORDER BY {sort} LIMIT ?',
        params + [limit]
    ).fetchall()

    output = args.output or 'export.csv'
    with open(output, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        for row in rows:
            writer.writerow(row)

    print(f'Экспортировано {len(rows)} записей в {output}')
    db.close()

def main():
    if not os.path.exists(DB_PATH):
        print(f'ERROR: Database not found: {DB_PATH}')
        print('Run "python import_to_db.py" first')
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Resume database CLI')
    sub = parser.add_subparsers(dest='cmd')

    p = sub.add_parser('найти', aliases=['find', 'f'])
    p.add_argument('query', nargs='?', help='Search query')
    p.add_argument('--телефон', '--phone', dest='phone')
    p.add_argument('--город', '--city', dest='city')
    p.add_argument('--метро', '--metro', dest='metro')
    p.add_argument('--пол', '--gender', dest='gender', choices=['Мужчина', 'Женщина'])
    p.add_argument('--возраст-от', '--age-from', dest='age_from', type=int)
    p.add_argument('--возраст-до', '--age-to', dest='age_to', type=int)
    p.add_argument('--стаж', '--experience', dest='experience', choices=['более 6 лет', '3-6 лет', '1-3 года'])
    p.add_argument('--стаж-от', '--exp-from', dest='exp_from', type=int, help='Мин. стаж в месяцах')
    p.add_argument('--образование', '--education', dest='education')
    p.add_argument('--зарплата-от', '--salary-from', dest='salary_from', type=int)
    p.add_argument('--зарплата-до', '--salary-to', dest='salary_to', type=int)
    p.add_argument('--занятость', '--employment', dest='employment')
    p.add_argument('--график', '--schedule', dest='schedule')
    p.add_argument('--командировки', '--business-trips', dest='business_trips', action='store_true')
    p.add_argument('--переезд', '--relocation', dest='relocation', action='store_true')
    p.add_argument('--права', '--license', dest='license')
    p.add_argument('--навыки', '--skills', dest='skills')
    p.add_argument('--навык', '--skill', dest='skill')
    p.add_argument('--компания', '--company', dest='company')
    p.add_argument('--валидные-контакты', '--valid-contacts', dest='valid_contacts', action='store_true')
    p.add_argument('--нрс', '--nrs', dest='nrs', choices=['yes', 'no'])
    p.add_argument('--накс', '--naks', dest='naks', choices=['yes', 'no'])
    p.add_argument('--nopriz', dest='nopriz', choices=['yes', 'no'])
    p.add_argument('--вик', '--vik', dest='vik', choices=['yes', 'no'])
    p.add_argument('--оттб', '--ottb', dest='ottb', choices=['yes', 'no'])
    p.add_argument('--ов', '--ov', dest='ov', choices=['yes', 'no'])
    p.add_argument('--мк', '--mk', dest='mk', choices=['yes', 'no'])
    p.add_argument('--вк', '--vk', dest='vk', choices=['yes', 'no'])
    p.add_argument('--эл', '--el', dest='el', choices=['yes', 'no'])
    p.add_argument('--сс', '--ss', dest='ss', choices=['yes', 'no'])
    p.add_argument('--лимит', '--limit', '-l', dest='limit', type=int, default=20)
    p.add_argument('--сортировка', '--sort', '-s', dest='sort', choices=['salary', 'age', 'exp', 'default'], default='default')
    p.add_argument('--файлы', '--files', dest='files', action='store_true')

    p = sub.add_parser('детально', aliases=['detail', 'd'])
    p.add_argument('id', type=int)
    p.add_argument('--файлы', '--files', dest='files', action='store_true')

    sub.add_parser('стата', aliases=['stats', 's'])

    p = sub.add_parser('файлы', aliases=['files'])
    p.add_argument('name', help='Name to search for')

    p = sub.add_parser('импорт', aliases=['import', 'imp'])
    p.add_argument('folder', nargs='?', help='Папка с PDF файлами резюме')

    p = sub.add_parser('экспорт', aliases=['export', 'exp'])
    p.add_argument('query', nargs='?', help='Search query')
    p.add_argument('--город', '--city', dest='city')
    p.add_argument('--метро', '--metro', dest='metro')
    p.add_argument('--зарплата-от', '--salary-from', dest='salary_from', type=int)
    p.add_argument('--зарплата-до', '--salary-to', dest='salary_to', type=int)
    p.add_argument('--стаж-от', '--exp-from', dest='exp_from', type=int)
    p.add_argument('--образование', '--education', dest='education')
    p.add_argument('--нрс', dest='nrs', choices=['yes', 'no'])
    p.add_argument('--накс', dest='naks', choices=['yes', 'no'])
    p.add_argument('--ноприз', dest='nopriz', choices=['yes', 'no'])
    p.add_argument('--навык', '--skill', dest='skill')
    p.add_argument('--компания', '--company', dest='company')
    p.add_argument('--валидные-контакты', '--valid-contacts', dest='valid_contacts', action='store_true')
    p.add_argument('--лимит', '--limit', dest='limit', type=int, default=1000)
    p.add_argument('--output', '-o', help='Имя выходного CSV файла')

    p = sub.add_parser('дубли', aliases=['duplicates', 'dup'])
    p.add_argument('--режим', '--mode', dest='mode', choices=['email', 'name', 'phone'], default='email')
    p.add_argument('--лимит', '--limit', dest='limit', type=int, default=50)

    p = sub.add_parser('слить', aliases=['merge'])
    p.add_argument('ids', help='ID записей через запятую (первый = основной)')

    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        return

    if args.cmd in ('найти', 'find', 'f'):
        cmd_find(args)
    elif args.cmd in ('детально', 'detail', 'd'):
        cmd_detail(args)
    elif args.cmd in ('стата', 'stats', 's'):
        cmd_stats(args)
    elif args.cmd in ('файлы', 'files'):
        cmd_files(args)
    elif args.cmd in ('импорт', 'import', 'imp'):
        cmd_import(args)
    elif args.cmd in ('экспорт', 'export', 'exp'):
        cmd_export(args)
    elif args.cmd in ('дубли', 'duplicates', 'dup'):
        cmd_duplicates(args)
    elif args.cmd in ('слить', 'merge'):
        cmd_merge(args)


def cmd_duplicates(args):
    """Показать дубликаты в базе."""
    db = get_db()
    mode = args.mode or 'email'

    if mode == 'email':
        cur = db.execute("""
            SELECT LOWER(email) as em, GROUP_CONCAT(row_id) as ids, COUNT(*) as cnt,
                   MIN(fio) as fio
            FROM resumes
            WHERE email IS NOT NULL AND email != '' AND email != 'None'
              AND email NOT LIKE '%Не найдено%'
            GROUP BY em
            HAVING cnt > 1
            ORDER BY cnt DESC
            LIMIT ?
        """, (args.limit or 50,))
    elif mode == 'name':
        cur = db.execute("""
            SELECT LOWER(TRIM(fio)) as fio_l, LOWER(TRIM(city_clean)) as city_l,
                   GROUP_CONCAT(row_id) as ids, COUNT(*) as cnt, MIN(fio) as fio
            FROM resumes
            WHERE fio IS NOT NULL AND fio != '' AND fio != 'None'
            GROUP BY fio_l, city_l
            HAVING cnt > 1
            ORDER BY cnt DESC
            LIMIT ?
        """, (args.limit or 50,))
    elif mode == 'phone':
        cur = db.execute("""
            SELECT phone_normalized as ph, GROUP_CONCAT(row_id) as ids, COUNT(*) as cnt,
                   MIN(fio) as fio
            FROM resumes
            WHERE phone_normalized IS NOT NULL AND phone_normalized != ''
            GROUP BY ph
            HAVING cnt > 1
            ORDER BY cnt DESC
            LIMIT ?
        """, (args.limit or 50,))
    else:
        print(f"Неизвестный режим: {mode}. Доступные: email, name, phone")
        db.close()
        return

    rows = cur.fetchall()
    print(f"Найдено групп дубликатов: {len(rows)}")
    print(f"Режим: {mode}\n")

    for row in rows:
        ids_str = str(row[1])
        ids = [int(x.strip()) for x in ids_str.split(',') if x.strip()]
        print(f"  {row[3]}: {len(ids)} записей")
        for rid in ids:
            detail = db.execute("SELECT row_id, fio, city, phone, email FROM resumes WHERE row_id = ?", (rid,)).fetchone()
            if detail:
                dup_info = db.execute("SELECT is_duplicate FROM resumes WHERE row_id = ?", (rid,)).fetchone()
                marker = " [ДУБЛИКАТ]" if dup_info and dup_info[0] else " [ОСНОВНОЙ]"
                print(f"    ID {detail[0]}: {detail[1]}, {detail[2]}, {detail[3]}, {detail[4]}{marker}")
        print()

    db.close()


def cmd_merge(args):
    """Слить дубликаты в одну запись."""
    db = get_db()
    ids = [int(x.strip()) for x in args.ids.split(',')]

    if len(ids) < 2:
        print("Нужно минимум 2 ID для слияния")
        db.close()
        return

    primary = ids[0]
    duplicates = ids[1:]

    primary_rec = db.execute("SELECT * FROM resumes WHERE row_id = ?", (primary,)).fetchone()
    if not primary_rec:
        print(f"Запись ID={primary} не найдена")
        db.close()
        return

    col_names = [desc[0] for desc in db.execute("SELECT * FROM resumes LIMIT 1").description]

    text_cols = ['fio', 'phone', 'email', 'telegram', 'whatsapp', 'skills', 'specialty',
                 'experience_and_education', 'additional_info', 'desired_position',
                 'city', 'city_clean', 'metro', 'citizenship', 'employment', 'schedule',
                 'relocation', 'business_trips', 'license_category', 'birth_date',
                 'resume_update_date']

    updates = {}
    for col in text_cols:
        if col not in col_names:
            continue
        best_val = primary_rec[col_names.index(col)]
        for dup_id in duplicates:
            dup_rec = db.execute(f"SELECT {col} FROM resumes WHERE row_id = ?", (dup_id,)).fetchone()
            if dup_rec and dup_rec[0]:
                val = dup_rec[0]
                if val and val != 'None' and val != '':
                    if not best_val or best_val == 'None' or best_val == '':
                        best_val = val
                    elif len(str(val)) > len(str(best_val)):
                        best_val = val
        if best_val and best_val != 'None':
            updates[col] = best_val

    num_cols = ['age', 'desired_salary', 'experience_months']
    for col in num_cols:
        if col not in col_names:
            continue
        best_val = primary_rec[col_names.index(col)]
        for dup_id in duplicates:
            dup_rec = db.execute(f"SELECT {col} FROM resumes WHERE row_id = ?", (dup_id,)).fetchone()
            if dup_rec and dup_rec[0]:
                best_val = dup_rec[0]
                break
        updates[col] = best_val

    set_clause = ', '.join(f'{col} = ?' for col in updates)
    values = list(updates.values())
    values.append(primary)
    db.execute(f"UPDATE resumes SET {set_clause} WHERE row_id = ?", values)

    for dup_id in duplicates:
        db.execute("UPDATE resumes SET is_duplicate = 1, duplicate_of = ? WHERE row_id = ?", (primary, dup_id))

    db.commit()
    print(f"Слито {len(duplicates)} дубликатов в ID={primary}")
    print(f"Обновлённые поля: {', '.join(updates.keys())}")
    db.close()


def cmd_import(args):
    from pdf_parser import extract_text_from_pdf, parse_hh_resume, normalize_phone

    folder = args.folder
    if not folder:
        folder = r''./pdfs/'

    if not os.path.isdir(folder):
        print(f'Папка не найдена: {folder}')
        return

    pdf_files = [f for f in os.listdir(folder) if f.lower().endswith('.pdf')]
    if not pdf_files:
        print(f'Нет PDF файлов в: {folder}')
        return

    print(f'Найдено PDF: {len(pdf_files)}')
    print(f'Папка: {folder}\n')

    db = get_db()
    imported = 0
    skipped = 0

    for pdf_file in pdf_files:
        pdf_path = os.path.join(folder, pdf_file)
        try:
            text = extract_text_from_pdf(pdf_path)
            data = parse_hh_resume(text, pdf_path)
            if not data.get('fio'):
                print(f'  SKIP (нет ФИО): {pdf_file}')
                skipped += 1
                continue

            fio = data['fio']
            phone_norm = normalize_phone(data.get('phone', ''))

            existing = None
            if phone_norm:
                existing = db.execute(
                    "SELECT row_id, fio, phone FROM resumes WHERE fio LIKE ? AND phone_normalized LIKE ?",
                    (f'%{fio}%', f'%{phone_norm}%')
                ).fetchone()

            if not existing:
                existing = db.execute(
                    "SELECT row_id, fio FROM resumes WHERE fio = ?",
                    (fio,)
                ).fetchone()

            if existing:
                print(f'  SKIP (дубликат ID={existing[0]}): {fio}')
                skipped += 1
                continue

            cols = [
                'fio', 'gender', 'age', 'birth_date', 'city', 'citizenship',
                'desired_position', 'desired_salary', 'experience',
                'education_category', 'employment', 'schedule',
                'relocation', 'business_trips', 'commute_time',
                'phone', 'email', 'telegram', 'whatsapp',
                'skills', 'specialty', 'experience_and_education',
                'additional_info', 'resume_update_date',
                'phone_normalized', 'license_category',
            ]
            placeholders = ','.join('?' for _ in cols)
            col_names = ','.join(cols)
            values = [
                data.get('fio', ''),
                data.get('gender', ''),
                data.get('age', ''),
                data.get('birth_date', ''),
                data.get('city', ''),
                data.get('citizenship', ''),
                data.get('desired_position', ''),
                data.get('desired_salary', ''),
                data.get('experience', ''),
                data.get('education_category', ''),
                data.get('employment', ''),
                data.get('schedule', ''),
                data.get('relocation', ''),
                data.get('business_trips', ''),
                data.get('commute_time', ''),
                data.get('phone', ''),
                data.get('email', ''),
                data.get('telegram', ''),
                data.get('whatsapp', ''),
                data.get('skills', ''),
                data.get('specialty', ''),
                data.get('experience_and_education', ''),
                data.get('additional_info', ''),
                data.get('resume_update_date', ''),
                phone_norm,
                data.get('license_category', ''),
            ]

            # Сертификаты
            for cert_key in ['nrs','naks','nopriz','vik','ottb','ov','mk','vk','el','ss']:
                if data.get(cert_key):
                    values.append('Есть')
                else:
                    values.append('')

            db.execute(f'INSERT INTO resumes ({col_names}) VALUES ({placeholders})', values)
            db.commit()
            imported += 1
            print(f'  OK: {fio} (phone: {data.get("phone", "—")}, city: {data.get("city", "—")})')
        except Exception as e:
            print(f'  ERROR: {pdf_file} — {e}')
            import traceback
            traceback.print_exc()

    db.close()
    print(f'\nИтого: импортировано {imported}, пропущено {skipped}')

    db.close()
    print(f'\nИтого: импортировано {imported}, пропущено {skipped}')


def parse_pdf_resume(pdf_path):
    from pypdf import PdfReader

    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    result = {}
    lines = text.split('\n')
    lines = [l.strip() for l in lines if l.strip()]

    # ФИО
    if lines:
        first = lines[0].strip()
        if len(first) < 80 and not any(kw in first.lower() for kw in ['резюме', 'обновлено']):
            result['fio'] = first

    # Пол, возраст
    for line in lines[:5]:
        gm = re.search(r'(Мужчина|Женщина)', line)
        if gm:
            result['gender'] = gm.group(1)
        am = re.search(r'(\d+)\s+лет', line)
        if am:
            result['age'] = am.group(1)
        if result.get('gender') and result.get('age'):
            break

    # Телефон
    pm = re.search(r'(\+7[\s\xa0\(\)\-0-9]{10,18})', text)
    result['phone'] = pm.group(1).strip() if pm else ''

    # Email
    em = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    result['email'] = em.group(1) if em else ''

    # Город
    cm = re.search(r'Проживает:\s*(.+?)(?:\n|$)', text)
    if cm:
        result['city'] = cm.group(1).strip().split(',')[0].strip()

    # Гражданство
    citm = re.search(r'Гражданство:\s*([^,\n]+)', text)
    if citm:
        result['citizenship'] = citm.group(1).strip()

    # Переезд
    rm = re.search(r'((?:Не\s+)?готов[ао]?\s+к\s+переезду)', text)
    if rm:
        result['relocation'] = rm.group(1).strip()

    # Командировки
    tm = re.search(r'((?:не\s+)?готов[ао]?\s+к\s+(?:редким\s+)?командировкам)', text, re.IGNORECASE)
    if tm:
        result['business_trips'] = tm.group(1).strip()

    # Должность
    dpm = re.search(r'Желаемая должность и зарплата\s*\n(.+?)(?:\n|$)', text)
    if dpm:
        result['desired_position'] = dpm.group(1).strip()

    # Зарплата
    sm = re.search(r'([\d\s]+)\s*₽', text)
    if sm:
        result['desired_salary'] = ''.join(c for c in sm.group(1) if c.isdigit())

    # Занятость
    epm = re.search(r'Занятость:\s*(.+?)(?:\n|$)', text)
    if epm:
        result['employment'] = epm.group(1).strip()

    # График
    scm = re.search(r'График работы:\s*(.+?)(?:\n|$)', text)
    if scm:
        result['schedule'] = scm.group(1).strip()

    # Стаж
    expm = re.search(r'Опыт работы\s*[—-]\s*(\d+\s+(?:лет|год|года)\s*(?:\d+\s*(?:месяцев|месяц|месяца))?)', text)
    if expm:
        result['experience'] = expm.group(1).strip()

    # Образование
    edum = re.search(r'Образование\s*\n\s*(Высшее|Неоконченное высшее|Среднее специальное|Среднее|Бакалавр|Магистр|Кандидат наук|Доктор наук)', text)
    if edum:
        result['education_category'] = edum.group(1)

    # Навыки
    skm = re.search(r'Навыки\s*\n(.+?)(?:Дополнительная информация|История общения|Обо мне|$)', text, re.DOTALL)
    if skm:
        result['skills'] = skm.group(1).strip()[:500]

    # Специализация
    spm = re.search(r'Специализации?:\s*\n(.+?)(?:\nЗанятость|\nГрафик|\nЖелательное|$)', text, re.DOTALL)
    if spm:
        result['specialty'] = spm.group(1).strip()[:300]

    return result


if __name__ == '__main__':
    main()
