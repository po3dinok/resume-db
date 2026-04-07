from pypdf import PdfReader
import sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

path = r"D:\ИНВЕНИУМ+\База резюме\Николаев Эдуард Николаевич.pdf"
if os.path.exists(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    
    # Search for the target text
    keywords = ["Бабушкина", "торгово-развлекательного", "150 тыс", "8 надземных", "подземного этажа", "демонтажа", "расчистки", "строительный объем"]
    
    print(f"File size: {len(text)} chars")
    print(f"\n=== Searching for keywords ===")
    for kw in keywords:
        if kw in text:
            idx = text.find(kw)
            print(f"\nFOUND '{kw}' at position {idx}:")
            print(f"  ...{text[max(0,idx-100):idx+len(kw)+200]}...")
        else:
            print(f"NOT FOUND: '{kw}'")
    
    # Also search for ТРЦ, торговый центр, многофункциональный
    extra = ["ТРЦ", "торговый центр", "торгово-развлекательный", "многофункциональный", "развлекательного центра"]
    print(f"\n=== Extra keywords ===")
    for kw in extra:
        if kw.lower() in text.lower():
            idx = text.lower().find(kw.lower())
            print(f"\nFOUND '{kw}' at position {idx}:")
            print(f"  ...{text[max(0,idx-100):idx+len(kw)+200]}...")
        else:
            print(f"NOT FOUND: '{kw}'")
else:
    print(f"File not found: {path}")
