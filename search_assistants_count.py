import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

print("=== Подсчёт ассистентов ===\n")

# Just count first
cur.execute("SELECT COUNT(*) FROM resumes WHERE desired_position LIKE '%ассистент%' AND is_duplicate = 0")
count = cur.fetchone()[0]
print(f"Ассистентов всего: {count}")

# Count remote
cur.execute("""
    SELECT COUNT(*) FROM resumes 
    WHERE desired_position LIKE '%ассистент%' 
    AND (schedule LIKE '%удален%' OR schedule LIKE '%удалён%' OR employment LIKE '%удален%')
    AND is_duplicate = 0
""")
remote_count = cur.fetchone()[0]
print(f"Ассистентов удалённо: {remote_count}")

# Get first 20 remote
print("\n=== Первые 20 удалённых ассистентов ===\n")
cur.execute("""
    SELECT row_id, fio, city_clean, desired_position
    FROM resumes 
    WHERE desired_position LIKE '%ассистент%' 
    AND (schedule LIKE '%удален%' OR schedule LIKE '%удалён%' OR employment LIKE '%удален%')
    AND is_duplicate = 0
    LIMIT 20
""")
rows = cur.fetchall()
for r in rows:
    print(f"  ID={r[0]}, {r[1]}, {r[2]}, {r[3]}")

conn.close()
