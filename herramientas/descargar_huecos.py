#!/usr/bin/env python3
"""
Descarga las fotos listadas en Inventario_Huecos_Bogota.xlsx, las organiza por
localidad y genera 100_Huecos_Bogota.zip.

Uso (con este script y el Excel en la misma carpeta):
    pip install requests openpyxl pillow
    python descargar_huecos.py

Por cada fila intenta primero la "URL imagen directa"; si falla o está vacía,
abre la página de la columna "URL" y toma su imagen principal (og:image).
Lo que no se pueda bajar queda anotado en descarga_log.csv, sin inventar nada.
"""
import csv
import html
import io
import re
import shutil
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

import requests
from openpyxl import load_workbook

try:
    from PIL import Image
except ImportError:  # sin Pillow se guarda el archivo en su formato original
    Image = None

AQUI = Path(__file__).resolve().parent
EXCEL = AQUI / "Inventario_Huecos_Bogota.xlsx"
RAIZ = AQUI / "100_Huecos_Bogota"
CARPETAS = [
    "Usaquen", "Chapinero", "Santa_Fe", "San_Cristobal", "Usme", "Tunjuelito",
    "Bosa", "Kennedy", "Fontibon", "Engativa", "Suba", "Barrios_Unidos",
    "Teusaquillo", "Los_Martires", "Antonio_Narino", "Puente_Aranda",
    "La_Candelaria", "Rafael_Uribe_Uribe", "Ciudad_Bolivar", "Sumapaz",
]
CABECERAS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept-Language": "es-CO,es;q=0.9",
}
OG = [
    re.compile(r'<meta[^>]+property=["\']og:image(?::secure_url)?["\'][^>]+content=["\']([^"\']+)', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image', re.I),
    re.compile(r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)', re.I),
]
MIN_BYTES = 5_000  # por debajo de esto suele ser un ícono o un píxel


def bajar_imagen(url, referer=None):
    """Devuelve (bytes, extensión) o lanza una excepción."""
    cab = dict(CABECERAS)
    if referer:
        cab["Referer"] = referer
    r = requests.get(url, headers=cab, timeout=30)
    r.raise_for_status()
    tipo = r.headers.get("Content-Type", "").split(";")[0].strip().lower()
    if not tipo.startswith("image/"):
        raise ValueError(f"no es una imagen ({tipo or 'sin tipo'})")
    if len(r.content) < MIN_BYTES:
        raise ValueError(f"imagen demasiado pequeña ({len(r.content)} bytes)")
    ext = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp",
           "image/gif": ".gif"}.get(tipo, ".img")
    return r.content, ext


def imagen_principal(pagina):
    r = requests.get(pagina, headers=CABECERAS, timeout=30)
    r.raise_for_status()
    for patron in OG:
        m = patron.search(r.text)
        if m:
            return urljoin(pagina, html.unescape(m.group(1)))
    raise ValueError("la página no declara imagen principal (og:image)")


def guardar(datos, ext, destino_sin_ext):
    """Guarda como .jpg si se puede convertir; si no, en el formato original."""
    if Image is not None:
        try:
            im = Image.open(io.BytesIO(datos))
            ancho, alto = im.size
            if ext != ".jpg":
                im = im.convert("RGB")
                salida = destino_sin_ext.with_suffix(".jpg")
                im.save(salida, "JPEG", quality=92)
            else:
                salida = destino_sin_ext.with_suffix(".jpg")
                salida.write_bytes(datos)
            return salida, f"{ancho}x{alto}"
        except Exception:
            pass
    salida = destino_sin_ext.with_suffix(ext)
    salida.write_bytes(datos)
    return salida, ""


def main():
    if not EXCEL.exists():
        sys.exit(f"No encuentro {EXCEL.name} junto a este script.")
    for c in CARPETAS:
        (RAIZ / c).mkdir(parents=True, exist_ok=True)

    hoja = load_workbook(EXCEL, read_only=True, data_only=True)["Inventario"]
    filas = list(hoja.iter_rows(values_only=True))
    col = {nombre: i for i, nombre in enumerate(filas[0])}
    log, ok = [], 0

    for f in filas[1:]:
        if not f or f[col["ID"]] is None:
            continue
        ident = int(f[col["ID"]])
        pagina = f[col["URL"]] or ""
        directa = f[col["URL imagen directa"]] or ""
        destino = (RAIZ / f[col["Archivo"]]).with_suffix("")
        estado, usada, medidas, archivo = "", "", "", ""
        intentos = [("directa", directa)] if directa else []
        intentos.append(("og:image", None))
        for origen, url in intentos:
            try:
                if url is None:
                    url = imagen_principal(pagina)
                datos, ext = bajar_imagen(url, referer=pagina)
                salida, medidas = guardar(datos, ext, destino)
                archivo = str(salida.relative_to(RAIZ))
                estado, usada = f"OK ({origen})", url
                ok += 1
                break
            except Exception as e:
                estado = f"FALLÓ: {e}"
        print(f"{ident:03d}  {estado}")
        log.append([ident, f[col["Localidad"]], archivo, estado, medidas, usada, pagina])
        time.sleep(1)  # pausa de cortesía entre peticiones

    with open(RAIZ / "descarga_log.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["ID", "Localidad", "Archivo", "Estado", "Tamaño (px)",
                    "URL de imagen usada", "Página de origen"])
        w.writerows(log)
    shutil.copy2(EXCEL, RAIZ / EXCEL.name)
    shutil.make_archive(str(AQUI / "100_Huecos_Bogota"), "zip", AQUI, RAIZ.name)
    print(f"\n{ok} de {len(log)} fotos descargadas.")
    print(f"ZIP: {AQUI / '100_Huecos_Bogota.zip'}")
    print("Revisa descarga_log.csv y mira cada foto antes de usarla (sobre todo las de nivel B).")


if __name__ == "__main__":
    main()
