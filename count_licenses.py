import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Значения в license_category ===")
cur.execute("""
    SELECT license_category, COUNT(*) as cnt 
    FROM resumes 
    GROUP BY license_category 
    ORDER BY cnt DESC
""")
for r in cur.fetchall():
    print(f"  '{r[0]}': {r[1]:,}")

conn.close()
