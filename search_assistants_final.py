import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db', timeout=10)
cur = conn.cursor()

# Create composite index for faster queries
cur.execute("CREATE INDEX IF NOT EXISTS idx_position_remote ON resumes(desired_position, schedule, employment, is_duplicate)")
conn.commit()
print("✅ Индекс idx_position_remote создан")

# Now get the list
cur.execute("""
    SELECT row_id, fio, city_clean, desired_position
    FROM resumes 
    WHERE desired_position LIKE '%ассистент%'
    AND (schedule LIKE '%удален%' OR employment LIKE '%удален%')
    AND is_duplicate = 0
""")
rows = cur.fetchall()

print(f"\n📊 Бизнес-ассистенты удалённо: {len(rows)}\n")

for r in rows:
    print(f"  ID={r[0]}, {r[1]}, {r[2]}, {r[3]}")

conn.close()
