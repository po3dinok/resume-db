import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

cur.execute("PRAGMA table_info(resumes)")
cols = [row[1] for row in cur.fetchall()]

print("=== Анализ бесполезных столбцов ===\n")

useless = []

for col in cols:
    # Check for mostly empty/null values
    cur.execute(f'SELECT COUNT(*) FROM resumes WHERE "{col}" IS NOT NULL AND "{col}" != \'\' AND "{col}" != \'Не найдено\'')
    filled = cur.fetchone()[0]
    
    cur.execute("SELECT COUNT(*) FROM resumes")
    total = cur.fetchone()[0]
    
    pct = filled / total * 100
    
    if pct < 5:
        useless.append((col, filled, pct))
        print(f"  ⚠️ {col}: заполнено {filled:,} ({pct:.1f}%)")
    
    # Check for constant values
    cur.execute(f'SELECT "{col}", COUNT(*) as cnt FROM resumes GROUP BY "{col}" ORDER BY cnt DESC LIMIT 1')
    top = cur.fetchone()
    if top[1] / total > 95:
        print(f"  ⚠️ {col}: 95%+ одно значение: '{str(top[0])[:50]}' ({top[1]:,})")

print(f"\n=== Кандидаты на удаление ({len(useless)}) ===")
for col, filled, pct in useless:
    print(f"  {col}: {filled:,} ({pct:.1f}%)")

conn.close()
