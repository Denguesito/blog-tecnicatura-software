from PIL import Image
from pathlib import Path

# Script simple para generar variantes webp
# Uso: python tools/resize_images.py

BASE = Path(__file__).resolve().parent.parent
IMG_DIR = BASE / 'static' / 'img'
OUT_DIR = IMG_DIR / 'variants'
OUT_DIR.mkdir(parents=True, exist_ok=True)

# tamaños deseados (ancho en px)
SIZES = [364, 720, 1280]

# imágenes a procesar (lista de nombres base)
TARGETS = [
    'proyectos.webp',
    'tutoriales.webp',
    'comunidad.webp',
    'banner-principal.webp'
]

QUALITY = 75

for name in TARGETS:
    src = IMG_DIR / name
    if not src.exists():
        print(f"No existe {src}, se salta")
        continue

    try:
        with Image.open(src) as im:
            im = im.convert('RGB')
            for w in SIZES:
                # calcular altura proporcional
                h = int(im.height * (w / im.width))
                resized = im.resize((w, h), Image.LANCZOS)
                out_name = f"{src.stem}-{w}.webp"
                out_path = OUT_DIR / out_name
                resized.save(out_path, 'WEBP', quality=QUALITY, method=6)
                print(f"Generada: {out_path.relative_to(BASE)}")
    except Exception as e:
        print(f"Error procesando {src}: {e}")

print('Finalizado')
