import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

cur.execute("""
    SELECT COUNT(*) FROM resumes 
    WHERE telegram IS NOT NULL AND telegram != '' AND telegram != 'Не найдено'
""")
count = cur.fetchone()[0]
print(f"📱 Telegram: {count:,} человек")

cur.execute("SELECT COUNT(*) FROM resumes")
total = cur.fetchone()[0]
print(f"📊 Всего в базе: {total:,}")
print(f"📈 Процент: {count/total*100:.1f}%")

conn.close()
