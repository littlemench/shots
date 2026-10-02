#!/usr/bin/env python3
"""Build the public site from the gallery prototype.

Copies design/prototype into site/, keeping site/CNAME, and includes only the
photo files that photos/_data.js actually references (so duplicates, hidden
blank frames and skipped rolls are never published).

Usage: python3 tools/build_site.py
"""
import json, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "design" / "prototype"
OUT = ROOT / "site"

cname = (OUT / "CNAME").read_text() if (OUT / "CNAME").exists() else None
if OUT.exists():
    shutil.rmtree(OUT)
(OUT / "photos").mkdir(parents=True)

html = (SRC / "gallery.html").read_text()
html = html.replace("<title>Shots — Gallery prototype</title>", "<title>Shots</title>")
(OUT / "index.html").write_text(html)
shutil.copytree(SRC / "assets", OUT / "assets")
shutil.copy(SRC / "photos.js", OUT / "photos.js")

data_js = (SRC / "photos" / "_data.js").read_text()
photos = json.loads(re.search(r"window.SHOTS_PHOTOS = (\[.*\]);", data_js, re.S).group(1))
(OUT / "photos" / "_data.js").write_text(data_js)
size = 0
for p in photos:
    for rel in p["src"].values():
        src = SRC / rel
        shutil.copy(src, OUT / rel)
        size += src.stat().st_size

if cname:
    (OUT / "CNAME").write_text(cname)
print(f"site/ built: {len(photos)} photos, {size / 1e6:.0f} MB of images")
