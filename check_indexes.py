import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

# Check existing indexes
cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='resumes'")
indexes = [row[0] for row in cur.fetchall()]
print(f"Индексы: {indexes}")

# Check if desired_position is indexed
has_idx = any('desired_position' in idx.lower() for idx in indexes)
print(f"Индекс на desired_position: {has_idx}")

# Create index if missing
if not has_idx:
    print("Создаю индекс на desired_position...")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_desired_position ON resumes(desired_position)")
    conn.commit()
    print("Индекс создан")

conn.close()
