import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

# Keep ID=171 (more recent: 18.07.2024), mark ID=14732 as duplicate
cur.execute("""
    UPDATE resumes 
    SET is_duplicate = 1, duplicate_of = 171 
    WHERE row_id = 14732
""")
conn.commit()

# Verify
cur.execute("SELECT row_id, fio, is_duplicate, duplicate_of FROM resumes WHERE row_id IN (171, 14732)")
for r in cur.fetchall():
    status = "ДУБЛИКАТ" if r[2] else "ОСНОВНОЙ"
    dup_info = f" -> ID={r[3]}" if r[3] else ""
    print(f"  {status}: ID={r[0]}, ФИО={r[1]}{dup_info}")

print(f"\nОбновлено строк: {cur.rowcount}")
conn.close()
