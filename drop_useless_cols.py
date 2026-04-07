import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

cols_to_drop = ['Unnamed: 39', 'phone_normalized']

for col in cols_to_drop:
    try:
        cur.execute(f'ALTER TABLE resumes DROP COLUMN "{col}"')
        conn.commit()
        print(f"✅ Столбец '{col}' удалён")
    except Exception as e:
        print(f"❌ Ошибка удаления '{col}': {e}")

# Verify
cur.execute("PRAGMA table_info(resumes)")
cols = [row[1] for row in cur.fetchall()]
print(f"\nОсталось столбцов: {len(cols)}")

conn.close()
