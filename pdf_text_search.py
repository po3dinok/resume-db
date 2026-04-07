#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Поиск по тексту из PDF резюме.
Стратегия: сначала ищем в базе по ключевым словам, затем проверяем PDF только релевантных кандидатов.

Использование:
    python pdf_text_search.py "текст из резюме"
    python pdf_text_search.py "8 надземных 1 подземного" --лимит 50
"""

import os
import sys
import io
import re
import sqlite3
import argparse
import time

from pypdf import PdfReader

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PDF_FOLDER = r"D:\ИНВЕНИУМ+\База резюме"
DB_PATH = r"D:\DevScripts\ResumeDB\resume.db"


def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.replace('\xa0', ' ').replace('\r\n', '\n')
    except Exception:
        return ""


def search_in_db(query):
    """Ищем кандидатов в базе по ключевым словам из запроса."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Разбиваем на слова (длинее 2 символов)
    words = [w.strip() for w in re.split(r'[\s,;]+', query) if len(w.strip()) > 2]

    if not words:
        conn.close()
        return []

    # Строим SQL: ищем по experience_and_education, additional_info, skills
    conditions = []
    params = []
    for word in words:
        conditions.append(f"(experience_and_education LIKE ? OR additional_info LIKE ? OR skills LIKE ? OR specialty LIKE ?)")
        params.extend([f'%{word}%', f'%{word}%', f'%{word}%', f'%{word}%'])

    query_sql = f"""
        SELECT DISTINCT row_id, fio, desired_position, city, phone, email, experience_and_education
        FROM resumes
        WHERE {' AND '.join(conditions)}
    """
    cur.execute(query_sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows


def search_pdfs(candidates, query_words):
    """Проверяем PDF кандидатов на наличие точного текста."""
    results = []

    for rid, fio, pos, city, phone, email, exp in candidates:
        fio_clean = ' '.join(fio.split())
        matching_pdfs = [f for f in os.listdir(PDF_FOLDER)
                        if f.lower().startswith(fio_clean.lower()) and f.lower().endswith('.pdf')]

        for pdf_file in matching_pdfs:
            path = os.path.join(PDF_FOLDER, pdf_file)
            text = extract_text_from_pdf(path)

            if not text:
                continue

            # Проверяем все слова запроса
            all_found = True
            contexts = []
            for word in query_words:
                idx = text.lower().find(word.lower())
                if idx >= 0:
                    ctx = text[max(0, idx - 80):idx + len(word) + 200]
                    contexts.append((word, ctx))
                else:
                    all_found = False

            # Показываем даже если не все слова найдены (частичное совпадение)
            if contexts:
                results.append({
                    'id': rid,
                    'fio': fio,
                    'pos': pos,
                    'city': city,
                    'phone': phone,
                    'email': email,
                    'file': pdf_file,
                    'all_found': all_found,
                    'contexts': contexts,
                })

    return results


def main():
    parser = argparse.ArgumentParser(description='Поиск по тексту PDF резюме')
    parser.add_argument('query', help='Текст или фраза из резюме для поиска')
    parser.add_argument('--лимит', '--limit', type=int, default=20, help='Лимит кандидатов из базы')
    args = parser.parse_args()

    query = args.query
    words = [w.strip() for w in re.split(r'[\s,;]+', query) if len(w.strip()) > 2]

    print(f"Запрос: {query}")
    print(f"Ключевые слова: {', '.join(words)}")
    print()

    # Step 1: Find candidates in DB
    start = time.time()
    print(f"Поиск в базе...")
    candidates = search_in_db(query)
    print(f"Найдено кандидатов в базе: {len(candidates)}")

    if not candidates:
        # Fallback: search by ANY word
        print("По точному совпадению не найдено. Ищу по отдельным словам...")
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        all_candidates = []
        for word in words:
            cur.execute("""
                SELECT row_id, fio, desired_position, city, phone, email, experience_and_education
                FROM resumes
                WHERE experience_and_education LIKE ?
                   OR additional_info LIKE ?
                   OR skills LIKE ?
                   OR specialty LIKE ?
                LIMIT ?
            """, (f'%{word}%', f'%{word}%', f'%{word}%', f'%{word}%', args.лимит))
            all_candidates.extend(cur.fetchall())

        # Deduplicate
        seen = set()
        candidates = []
        for c in all_candidates:
            if c[0] not in seen:
                seen.add(c[0])
                candidates.append(c)
        conn.close()
        print(f"Найдено по отдельным словам: {len(candidates)}")

    if not candidates:
        print("\nНичего не найдено в базе.")
        return

    # Step 2: Scan PDFs of these candidates
    print(f"\nПроверка PDF файлов...")
    results = search_pdfs(candidates, words)

    # Sort: exact matches first
    results.sort(key=lambda x: (-int(x['all_found']), -len(x['contexts'])))

    elapsed = time.time() - start
    print(f"\n{'='*70}")
    print(f"РЕЗУЛЬТАТЫ ({len(results)} файлов, {elapsed:.1f}с)")
    print(f"{'='*70}")

    for r in results:
        status = "ТОЧНОЕ" if r['all_found'] else "ЧАСТИЧНОЕ"
        print(f"\n[{status}] ID: {r['id']}, ФИО: {r['fio']}")
        print(f"  Должность: {r['pos']}")
        print(f"  Город: {r['city']}")
        print(f"  Телефон: {r['phone']}")
        print(f"  Email: {r['email']}")
        print(f"  Файл: {r['file']}")
        for word, ctx in r['contexts']:
            print(f"  [{word}] ...{ctx}...")


if __name__ == '__main__':
    main()
