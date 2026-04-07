import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db')
cur = conn.cursor()

# Drop the index first
try:
    cur.execute("DROP INDEX IF EXISTS idx_phone_normalized")
    conn.commit()
    print("✅ Индекс idx_phone_normalized удалён")
except Exception as e:
    print(f"❌ Ошибка удаления индекса: {e}")

# Now drop the column
try:
    cur.execute('ALTER TABLE resumes DROP COLUMN "phone_normalized"')
    conn.commit()
    print("✅ Столбец 'phone_normalized' удалён")
except Exception as e:
    print(f"❌ Ошибка удаления столбца: {e}")

# Verify
cur.execute("PRAGMA table_info(resumes)")
cols = [row[1] for row in cur.fetchall()]
print(f"\nОсталось столбцов: {len(cols)}")

conn.close()
