#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Обновляет поле experience_and_education в базе полным текстом из PDF.
Извлекает секцию "Опыт работы" и "Образование" из PDF и сохраняет в БД.
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


def extract_full_text_from_pdf(pdf_path):
    """Извлекает полный текст из PDF."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.replace('\xa0', ' ').replace('\r\n', '\n')
    except Exception:
        return ""


def extract_experience_section(text):
    """Извлекает секцию опыта работы и образования из полного текста PDF."""
    idx1 = text.find('Опыт работы')
    idx2 = text.find('Образование')
    if idx1 >= 0 and idx2 > idx1:
        return text[idx1:idx2].strip()
    # Fallback: try "Навыки" as end marker
    idx3 = text.find('Навыки')
    if idx1 >= 0 and idx3 > idx1:
        return text[idx1:idx3].strip()
    return ""


def main():
    parser = argparse.ArgumentParser(description='Обновить опыт из PDF в базу')
    parser.add_argument('--id', type=int, help='Обновить конкретного кандидата по ID')
    parser.add_argument('--все', '--all', action='store_true', help='Обновить всех кандидатов')
    parser.add_argument('--файл', '--file', help='Обновить из конкретного PDF файла')
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if args.файл:
        # Update from specific file
        fio_from_file = os.path.splitext(os.path.basename(args.файл))[0].strip()
        text = extract_full_text_from_pdf(args.файл)
        if not text:
            print(f"Не удалось извлечь текст из {args.файл}")
            return

        exp_text = extract_experience_section(text)
        if not exp_text:
            exp_text = text[:3000]  # Fallback: first 3000 chars

        cursor.execute("""
            UPDATE resumes SET experience_and_education = ?
            WHERE fio LIKE ?
        """, (exp_text, f'%{fio_from_file}%'))
        conn.commit()
        updated = cursor.rowcount
        print(f"Обновлено записей: {updated}")

    elif args.id:
        # Update specific candidate
        cursor.execute("SELECT fio FROM resumes WHERE row_id = ?", (args.id,))
        row = cursor.fetchone()
        if not row:
            print(f"Кандидат ID={args.id} не найден")
            return

        fio = row[0]
        fio_clean = ' '.join(fio.split())
        matching_pdfs = [f for f in os.listdir(PDF_FOLDER)
                        if f.lower().startswith(fio_clean.lower()) and f.lower().endswith('.pdf')]

        if not matching_pdfs:
            print(f"PDF файл не найден для: {fio}")
            return

        pdf_path = os.path.join(PDF_FOLDER, matching_pdfs[0])
        text = extract_full_text_from_pdf(pdf_path)
        if not text:
            print(f"Не удалось извлечь текст из {matching_pdfs[0]}")
            return

        exp_text = extract_experience_section(text)
        if not exp_text:
            exp_text = text[:3000]

        cursor.execute("""
            UPDATE resumes SET experience_and_education = ?
            WHERE row_id = ?
        """, (exp_text, args.id))
        conn.commit()
        print(f"Обновлен ID={args.id}, ФИО={fio}")
        print(f"Новый текст опыта ({len(exp_text)} символов):")
        print(exp_text[:500])

    elif args.все:
        # Update all candidates
        cursor.execute("SELECT row_id, fio FROM resumes")
        all_candidates = cursor.fetchall()
        print(f"Всего кандидатов: {len(all_candidates)}")

        updated = 0
        skipped = 0
        start = time.time()

        for i, (rid, fio) in enumerate(all_candidates):
            fio_clean = ' '.join(fio.split())
            matching_pdfs = [f for f in os.listdir(PDF_FOLDER)
                            if f.lower().startswith(fio_clean.lower()) and f.lower().endswith('.pdf')]

            if not matching_pdfs:
                skipped += 1
                continue

            pdf_path = os.path.join(PDF_FOLDER, matching_pdfs[0])
            text = extract_full_text_from_pdf(pdf_path)
            if not text:
                skipped += 1
                continue

            exp_text = extract_experience_section(text)
            if not exp_text:
                exp_text = text[:3000]

            cursor.execute("""
                UPDATE resumes SET experience_and_education = ?
                WHERE row_id = ?
            """, (exp_text, rid))
            updated += 1

            if (i + 1) % 1000 == 0:
                elapsed = time.time() - start
                print(f"  Processed {i+1}/{len(all_candidates)}, updated: {updated} ({elapsed:.0f}s)")

        conn.commit()
        elapsed = time.time() - start
        print(f"\nГотово! Обновлено: {updated}, пропущено: {skipped}, время: {elapsed:.0f}s")

    else:
        parser.print_help()

    conn.close()


if __name__ == '__main__':
    main()
