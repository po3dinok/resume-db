import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db', timeout=10)
cur = conn.cursor()

cur.execute("""
    SELECT COUNT(*) FROM resumes 
    WHERE desired_position LIKE '%ассистент%' AND is_duplicate = 0
""")
print(f"Ассистентов: {cur.fetchone()[0]}")

cur.execute("""
    SELECT COUNT(*) FROM resumes 
    WHERE desired_position LIKE '%ассистент%'
    AND (schedule LIKE '%удален%' OR employment LIKE '%удален%')
    AND is_duplicate = 0
""")
print(f"Удалённо: {cur.fetchone()[0]}")

conn.close()
