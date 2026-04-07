#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Парсер PDF-резюме формата hh.ru. Извлекает ВСЕ поля для импорта в resume.db.
"""

import os
import re
import sys
import io

from pypdf import PdfReader


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


def parse_hh_resume(text, pdf_path=''):
    """Полный парсер резюме hh.ru — извлекает все доступные поля."""
    text = text.replace('\xa0', ' ')

    r = {}
    lines = text.split('\n')
    lines = [l.strip() for l in lines if l.strip()]

    # === ФИО ===
    if pdf_path:
        filename_base = os.path.splitext(os.path.basename(pdf_path))[0]
        filename_base = ' '.join(filename_base.split())
        if filename_base and len(filename_base) > 3:
            r['fio'] = filename_base

    if not r.get('fio') and lines:
        first = lines[0]
        first = re.sub(r'\s*(Мужчина|Женщина)\s*$', '', first).strip()
        if re.match(r'^[А-ЯЁ][а-яё\s\.]+$', first) and len(first) < 80 and len(first) > 3:
            r['fio'] = first

    # === Пол, возраст, дата рождения ===
    r['gender'] = ''
    r['age'] = ''
    r['birth_date'] = ''

    for line in lines[:8]:
        if not r['gender']:
            gm = re.search(r'(Мужчина|Женщина)', line)
            if gm:
                r['gender'] = gm.group(1)
        if not r['age']:
            am = re.search(r'(\d+)\s+лет', line)
            if am:
                r['age'] = am.group(1)
        if not r['birth_date']:
            bm = re.search(r'родился?\s+(.+?)(?:\n|$)', line)
            if bm:
                r['birth_date'] = bm.group(1).strip()

    # === Телефон ===
    phones = re.findall(r'(\+7[\s\(\)\-0-9]{10,18})', text)
    r['phone'] = phones[0].strip() if phones else ''

    # === Email ===
    em = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    r['email'] = em.group(1) if em else ''

    # === Telegram ===
    tg_match = re.search(r'Телеграм:\s*(@\S+)', text)
    r['telegram'] = tg_match.group(1).strip() if tg_match else ''

    # === WhatsApp ===
    wa_match = re.search(r'WhatsApp.*?(\+7[\d\s\(\)-]{10,})', text, re.IGNORECASE)
    r['whatsapp'] = wa_match.group(1).strip() if wa_match else ''

    # === Город ===
    city_match = re.search(r'Проживает:\s*(.+?)(?:\n|$)', text)
    if city_match:
        city_val = city_match.group(1).strip()
        r['city'] = city_val.split(',')[0].strip()

    # === Гражданство ===
    cit_match = re.search(r'Гражданство:\s*([^,\n]+)', text)
    if cit_match:
        r['citizenship'] = cit_match.group(1).strip()

    # === Переезд ===
    reloc_match = re.search(r'((?:Не\s+)?готов[ао]?\s+к\s+переезду)', text)
    if reloc_match:
        r['relocation'] = reloc_match.group(1).strip()
    if not r.get('relocation'):
        reloc_match2 = re.search(r'Готов к переезду:', text)
        if reloc_match2:
            r['relocation'] = 'Готов к переезду'

    # === Командировки ===
    trip_match = re.search(r'((?:не\s+)?готов[ао]?\s+к\s+(?:редким\s+)?командировкам)', text, re.IGNORECASE)
    if trip_match:
        r['business_trips'] = trip_match.group(1).strip()

    # === Желаемая должность ===
    pos_match = re.search(r'Желаемая должность и зарплата\s*\n(.+?)(?:\n|$)', text)
    if pos_match:
        r['desired_position'] = pos_match.group(1).strip()

    # === Специализация ===
    spec_match = re.search(r'Специализации?:\s*\n(.+?)(?:\nЗанятость|\nГрафик|\nЖелательное|$)', text, re.DOTALL)
    if spec_match:
        r['specialty'] = spec_match.group(1).strip()

    # === Занятость ===
    emp_match = re.search(r'Занятость:\s*(.+?)(?:\n|$)', text)
    if emp_match:
        r['employment'] = emp_match.group(1).strip()

    # === График ===
    sched_match = re.search(r'График работы:\s*(.+?)(?:\n|$)', text)
    if sched_match:
        r['schedule'] = sched_match.group(1).strip()

    # === Желательное время в пути ===
    commute_match = re.search(r'Желательное время в пути до работы:\s*(.+?)(?:\n|$)', text)
    if commute_match:
        r['commute_time'] = commute_match.group(1).strip()

    # === Зарплата ===
    salary_match = re.search(r'([\d\s]+)\s*₽', text)
    if salary_match:
        digits = ''.join(c for c in salary_match.group(1) if c.isdigit())
        if digits:
            r['desired_salary'] = digits

    # === Опыт работы (общий стаж) ===
    exp_match = re.search(r'Опыт работы\s*[—-]\s*(\d+\s+(?:лет|год|года)\s*(?:\d+\s*(?:месяцев|месяц|месяца))?)', text)
    if exp_match:
        r['experience'] = exp_match.group(1).strip()

    # === Образование (уровень) ===
    edu_match = re.search(r'(?:Образование\s*\n\s*Уровень\s*)?(Высшее|Неоконченное высшее|Среднее специальное|Среднее образование|Среднее|Бакалавр|Магистр|Кандидат наук|Доктор наук)', text)
    if edu_match:
        edu_val = edu_match.group(1)
        if edu_val == 'Среднее образование':
            edu_val = 'Среднее'
        r['education_category'] = edu_val

    # === Опыт работы и образование (полный текст) ===
    exp_section = re.search(r'Опыт работы\s*\n(.+?)(?=Образование\n|Ключевые навыки\n|Навыки\n|$)', text, re.DOTALL)
    if exp_section:
        exp_text = exp_section.group(1).strip()
        exp_text = re.sub(r'Резюме обновлено.+?\n?', '', exp_text)
        r['experience_and_education'] = exp_text[:2000]

    edu_section = re.search(r'Образование\s*\n(.+?)(?=Ключевые навыки\n|Навыки\n|Дополнительная информация\n|Тесты, экзамены\n|$)', text, re.DOTALL)
    if edu_section:
        edu_text = edu_section.group(1).strip()
        edu_text = re.sub(r'Резюме обновлено.+?\n?', '', edu_text)
        if 'experience_and_education' not in r:
            r['experience_and_education'] = edu_text[:2000]
        else:
            r['experience_and_education'] += '\n\n' + edu_text[:1000]

    # === Навыки ===
    skills_match = re.search(r'Навыки\s*\n(.+?)(?=Дополнительная информация\n|История общения\n|Обо мне\n|$)', text, re.DOTALL)
    if skills_match:
        skills_text = skills_match.group(1).strip()
        skills_text = re.sub(r'Знание языков\s*.+?(?:\n|$)', '', skills_text)
        skills_text = re.sub(r'^Навыки\s+', '', skills_text)
        r['skills'] = skills_text.strip()[:1000]

    # === Дополнительная информация / Обо мне ===
    about_match = re.search(r'Дополнительная информация\s*\n(?:Обо мне\s*)?(.+?)(?=История общения\n|История общения\s|$)', text, re.DOTALL)
    if about_match:
        about_text = about_match.group(1).strip()
        about_text = re.sub(r'Резюме обновлено.+?\n?', '', about_text)
        about_text = re.sub(r'^[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s*•\s*', '', about_text)
        about_text = re.sub(r'^\d+\s+\S+\s+\d+\s+в\s+\d+:\d+\s*Обо мне\s*', '', about_text)
        about_text = re.sub(r'^Обо мне\s*', '', about_text)
        r['additional_info'] = about_text.strip()[:2000]

    # === Дата обновления резюме ===
    update_match = re.search(r'Резюме обновлено\s+(\d+\s+\S+\s+\d+)', text)
    if update_match:
        r['resume_update_date'] = update_match.group(1).strip()

    # === Сертификаты ===
    certs_map = {
        'nrs': r'(?:НРС|Национальный реестр специалистов)',
        'naks': r'НАКС',
        'nopriz': r'(?:НОПРИЗ|Национальное объединение изыскателей)',
        'vik': r'ВИК',
        'ottb': r'(?:ОТТБ|Охрана труда)',
        'ov': r'(?:ОВ\s*—|Отопление и вентиляция)',
        'mk': r'(?:МК\s*—|Металлические конструкции)',
        'vk': r'(?:ВК\s*—|Водоснабжение и канализация)',
        'el': r'(?:ЭЛ\s*—|Электроснабжение)',
        'ss': r'(?:СС\s*—|Системы связи)',
    }
    for cert_key, pat in certs_map.items():
        if re.search(pat, text, re.IGNORECASE):
            r[cert_key] = 'Есть'

    # === Права ===
    license_match = re.search(r'Водительское удостоверение[:\s]*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if license_match:
        r['license_category'] = license_match.group(1).strip()

    return r


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


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Парсер PDF-резюме hh.ru')
    parser.add_argument('folder', nargs='?', default=None, help='Папка с PDF файлами')
    parser.add_argument('--файл', '--file', dest='single_file', help='Один PDF файл')
    parser.add_argument('--json', action='store_true', help='Вывод в JSON')
    args = parser.parse_args()

    folder = args.folder or './pdfs/'

    if args.single_file:
        pdf_files = [args.single_file]
    elif os.path.isdir(folder):
        pdf_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith('.pdf')]
    else:
        print(f"Папка не найдена: {folder}")
        return

    print(f"Найдено PDF файлов: {len(pdf_files)}\n")

    all_results = []
    for pdf_path in pdf_files:
        try:
            text = extract_text_from_pdf(pdf_path)
            result = parse_hh_resume(text, pdf_path)
            result['file'] = os.path.basename(pdf_path)
            result['phone_normalized'] = normalize_phone(result.get('phone', ''))
            all_results.append(result)

            if not args.json:
                print(f"{'='*70}")
                print(f"Файл: {result['file']}")
                print(f"  ФИО:            {result.get('fio', '')}")
                print(f"  Телефон:        {result.get('phone', '')}")
                print(f"  Email:          {result.get('email', '')}")
                print(f"  Telegram:       {result.get('telegram', '')}")
                print(f"  Должность:      {result.get('desired_position', '')}")
                print(f"  Специальность:  {result.get('specialty', '')}")
                print(f"  Город:          {result.get('city', '')}")
                print(f"  Зарплата:       {result.get('desired_salary', '')}")
                print(f"  Стаж:           {result.get('experience', '')}")
                print(f"  Образование:    {result.get('education_category', '')}")
                print(f"  Пол:            {result.get('gender', '')}")
                print(f"  Возраст:        {result.get('age', '')}")
                print(f"  Дата рождения:  {result.get('birth_date', '')}")
                print(f"  Гражданство:    {result.get('citizenship', '')}")
                print(f"  Занятость:      {result.get('employment', '')}")
                print(f"  График:         {result.get('schedule', '')}")
                print(f"  Время в пути:   {result.get('commute_time', '')}")
                print(f"  Переезд:        {result.get('relocation', '')}")
                print(f"  Командировки:   {result.get('business_trips', '')}")
                print(f"  Права:          {result.get('license_category', '')}")
                certs = [k.upper() for k in ['nrs','naks','nopriz','vik','ottb','ov','mk','vk','el','ss'] if result.get(k)]
                print(f"  Сертификаты:    {', '.join(certs) if certs else 'Нет'}")
                print(f"  Обновлено:      {result.get('resume_update_date', '')}")
                if result.get('skills'):
                    print(f"  Навыки:         {result['skills'][:150]}...")
                if result.get('additional_info'):
                    print(f"  Обо мне:        {result['additional_info'][:150]}...")
                print()
        except Exception as e:
            print(f"Ошибка при обработке {os.path.basename(pdf_path)}: {e}")
            import traceback
            traceback.print_exc()

    if args.json:
        import json
        print(json.dumps(all_results, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
