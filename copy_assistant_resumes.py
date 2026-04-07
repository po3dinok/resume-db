import sqlite3
import os
import glob
import shutil
import zipfile
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect(r'D:\DevScripts\ResumeDB\resume.db', timeout=10)
cur = conn.cursor()

# Get IDs
cur.execute("""
    SELECT row_id, fio FROM resumes 
    WHERE schedule LIKE '%удален%'
    AND desired_position LIKE '%ассистент%'
    AND is_duplicate = 0
""")
rows = cur.fetchall()

source_dir = r"D:\ИНВЕНИУМ+\База резюме"
desktop_dir = r"./output"
output_folder = os.path.join(desktop_dir, "Бизнес-ассистенты_удалённо")
zip_path = os.path.join(desktop_dir, "Бизнес-ассистенты_удалённо.zip")

# Create output folder
if os.path.exists(output_folder):
    shutil.rmtree(output_folder)
os.makedirs(output_folder)

print(f"📁 Копирую резюме в: {output_folder}\n")

copied = 0
not_found = 0

for row_id, fio in rows:
    # Clean filename
    clean_name = fio.replace('/', '_').replace('\\', '_').replace(':', '_').replace('*', '_').replace('?', '_').replace('"', '_').replace('<', '_').replace('>', '_').replace('|', '_')
    
    # Search for PDF
    pattern = os.path.join(source_dir, f"{clean_name}*.pdf")
    files = glob.glob(pattern)
    
    if files:
        src = files[0]
        dst = os.path.join(output_folder, f"{clean_name}.pdf")
        shutil.copy2(src, dst)
        copied += 1
    else:
        # Try with underscores
        pattern2 = os.path.join(source_dir, f"{clean_name.replace(' ', '_')}*.pdf")
        files2 = glob.glob(pattern2)
        if files2:
            src = files2[0]
            dst = os.path.join(output_folder, f"{clean_name}.pdf")
            shutil.copy2(src, dst)
            copied += 1
        else:
            not_found += 1
            print(f"  ❌ Не найден: {fio}")

print(f"\n✅ Скопировано: {copied}")
print(f"❌ Не найдено: {not_found}")

# Create zip archive
print(f"\n📦 Создаю архив: {zip_path}")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(output_folder):
        for file in files:
            file_path = os.path.join(root, file)
            arcname = os.path.relpath(file_path, output_folder)
            zipf.write(file_path, arcname)

zip_size = os.path.getsize(zip_path) / (1024 * 1024)
print(f"✅ Архив создан: {zip_size:.1f} МБ")

conn.close()
