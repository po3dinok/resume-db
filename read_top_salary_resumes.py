import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from pypdf import PdfReader

files = [
    r"D:\ИНВЕНИУМ+\База резюме\Belavsky Vadim Arkadyevich.pdf",
    r"D:\ИНВЕНИУМ+\База резюме\Sokolov Viktor.pdf",
    r"D:\ИНВЕНИУМ+\База резюме\Абакарова Захра Тимуровна.pdf",
    r"D:\ИНВЕНИУМ+\База резюме\Абхазава Георгий Мерабович.pdf",
    r"D:\ИНВЕНИУМ+\База резюме\Азимов Тимур Георгиевич.pdf",
    r"D:\ИНВЕНИУМ+\База резюме\Андреев Макс.pdf",
    r"D:\ИНВЕНИУМ+\База резюме\Артюхов Виктор Валерьевич.pdf",
    r"D:\ИНВЕНИУМ+\База резюме\Ахмедов Фархад Алиискендер.pdf",
    r"D:\ИНВЕНИУМ+\База резюме\Бабичев Александр Вячеславович.pdf",
    r"D:\ИНВЕНИУМ+\База резюме\Базыль Дмитрий Валерьевич.pdf",
]

for fpath in files:
    name = fpath.split("\\")[-1].replace(".pdf", "")
    print(f"\n{'='*60}")
    print(f"👤 {name}")
    print(f"{'='*60}")
    
    try:
        reader = PdfReader(fpath)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                print(f"\n{text[:3000]}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "-"*60)
