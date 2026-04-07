import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Бизнес-ассистенты (удалённо) ===\n")

# Use FTS5 for faster search
cur.execute("""
    SELECT r.row_id, r.fio, r.city_clean, r.desired_position, r.schedule, r.employment
    FROM resumes r
    JOIN resume_fts f ON r.row_id = f.rowid
    WHERE resume_fts MATCH 'ассистент OR помощник'
    AND (r.schedule LIKE '%удален%' OR r.schedule LIKE '%удалён%' OR r.employment LIKE '%удален%')
    AND r.is_duplicate = 0
    LIMIT 50
""")
rows = cur.fetchall()

print(f"Найдено: {len(rows)} кандидатов\n")

for r in rows:
    print(f"  ID={r[0]}, {r[1]}, {r[2]}")
    print(f"    {r[3]}")
    print()

conn.close()
