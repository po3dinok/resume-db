import os
import glob

source_dir = r"D:\ИНВЕНИУМ+\База резюме"

candidates = [
    "Belavsky Vadim",
    "Sokolov Viktor",
    "Абакарова Захра",
    "Абхазава Георгий",
    "Азимов Тимур",
    "Андреев Макс",
    "Артюхов Виктор",
    "Ахмедов Фархад",
    "Бабичев Александр",
    "Базыль Дмитрий"
]

print("=== Поиск PDF файлов кандидатов ===\n")

found_files = {}

for name in candidates:
    # Search for files starting with the name
    pattern = os.path.join(source_dir, f"{name}*.pdf")
    files = glob.glob(pattern)
    if files:
        print(f"✅ {name}: {files[0]}")
        found_files[name] = files[0]
    else:
        # Try alternative search if exact match fails (e.g. spaces vs underscores)
        pattern2 = os.path.join(source_dir, f"{name.replace(' ', '_')}*.pdf")
        files2 = glob.glob(pattern2)
        if files2:
            print(f"✅ {name}: {files2[0]}")
            found_files[name] = files2[0]
        else:
            print(f"❌ {name}: Не найден файл")

print(f"\nНайдено файлов: {len(found_files)}")
