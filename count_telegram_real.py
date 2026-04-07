import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Значения в колонке telegram ===")
cur.execute("""
    SELECT telegram, COUNT(*) as cnt 
    FROM resumes 
    GROUP BY telegram 
    ORDER BY cnt DESC 
    LIMIT 20
""")
for r in cur.fetchall():
    print(f"  '{r[0][:80]}': {r[1]:,}")

print("\n=== Реальные ссылки t.me ===")
cur.execute("""
    SELECT COUNT(*) FROM resumes 
    WHERE telegram LIKE '%t.me%'
""")
real = cur.fetchone()[0]
print(f"  Реальные ссылки: {real:,}")

cur.execute("SELECT COUNT(*) FROM resumes")
total = cur.fetchone()[0]
print(f"  Всего: {total:,}")
print(f"  Процент: {real/total*100:.1f}%")

conn.close()
