import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Get both records
cur.execute("SELECT * FROM resumes WHERE row_id IN (171, 14732)")
rows = cur.fetchall()

for r in rows:
    print(f"\n=== ID={r['row_id']}, ФИО={r['fio']} ===")
    for key in r.keys():
        val = r[key]
        if val is not None and str(val).strip():
            print(f"  {key}: {val}")

conn.close()
