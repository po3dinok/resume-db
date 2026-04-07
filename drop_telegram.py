import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

# Check SQLite version
cur.execute("SELECT sqlite_version()")
version = cur.fetchone()[0]
print(f"SQLite версия: {version}")

# Drop the telegram column
try:
    cur.execute("ALTER TABLE resumes DROP COLUMN telegram")
    conn.commit()
    print("✅ Столбец telegram удалён")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# Verify
cur.execute("PRAGMA table_info(resumes)")
cols = [row[1] for row in cur.fetchall()]
print(f"\nСтолбцы ({len(cols)}): {', '.join(cols)}")

conn.close()
