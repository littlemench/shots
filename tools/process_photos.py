#!/usr/bin/env python3
"""Turn a folder of photos into gallery data.

Reads   design/photos/<folder>/...       (your library; folder names are the metadata)
Writes  design/prototype/photos/<id>-s.jpg, <id>-l.jpg   (web copies, 800px / 2000px)
        design/prototype/photos/_data.js                 (what the gallery loads)
        design/photos/_shots-review.json                  (per-photo decisions: rotation,
                                                           types, hidden, status)

Photo ids come from the file's contents, so renaming or moving folders never loses
decisions. Review decisions from an older library file can be carried over with
--carry-over <path-to-old-review.json>.

Usage: .venv/bin/python tools/process_photos.py [--carry-over design/sample-photos/_shots-review.json]
Needs Pillow.
"""
import argparse, colorsys, hashlib, json, re
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
LIBRARY = ROOT / "design" / "photos"
OUT = ROOT / "design" / "prototype" / "photos"
REVIEW = LIBRARY / "_shots-review.json"
PHOTOGRAPHER = "Alex Menczykowski"

# ---- Folder-name rules -------------------------------------------------------
# First match wins. Patterns are case-insensitive and also catch common typos.
CAMERAS = [
    (r"mju\s*i?ii|mjuii|olympus", "Olympus Mju II"),
    (r"n[iI]kon", "Nikon FM"),
    (r"zenit\s*11", "Zenit 11"),
    (r"polar(oi|io)d", "Polaroid 340AF"),
]
# Place names found in folder names -> Location filter values
PLACES = {
    "Bude": ["Bude"], "Greece": ["Greece"], "Houston": ["Houston"], "Northampton": ["Northampton"],
    "Basque Country": ["Basque Country"], "Norfolk": ["Norfolk"], "Crete": ["Crete"],
    "LA": ["Los Angeles"], "Ibiza": ["Ibiza"], "Mallorca": ["Mallorca"], "Menorca": ["Menorca"],
    "Puglia": ["Puglia"], "Walthamstow": ["London"], "Shoreditch": ["London"], "Berlin": ["Berlin"],
    "London": ["London"], "Massachusetts": ["Massachusetts"], "New York": ["New York"], "Seville": ["Seville"],
}
# Two-tier locations: place -> country. A folder naming only a country gets no place.
COUNTRIES = {
    "Bude": "UK", "Northampton": "UK", "Norfolk": "UK", "London": "UK",
    "Greece": "Greece", "Crete": "Greece",
    "Houston": "USA", "Los Angeles": "USA", "Massachusetts": "USA", "New York": "USA",
    "Basque Country": "Spain", "Ibiza": "Spain", "Mallorca": "Spain", "Menorca": "Spain", "Seville": "Spain",
    "Puglia": "Italy", "Berlin": "Germany",
}
# Public album names: overrides for folder names that shouldn't be shown as-is
ALBUM_RENAMES = {"LA (Kobalt 2025)": "Los Angeles 2025"}
SKIP_FOLDERS = re.compile(r"(^|/)test(/|$)", re.I)
BW_FOLDER = re.compile(r"^(b&w|bw|black ?& ?white)$", re.I)


def parse_folder(top: str) -> dict:
    name = re.sub(r"\s+", " ", top).strip()
    camera = next((c for pat, c in CAMERAS if re.search(pat, name, re.I)), None)
    year = re.search(r"\b(19|20)\d\d\b", name)
    locations = []
    for key, vals in PLACES.items():
        if re.search(rf"\b{re.escape(key)}\b", name):
            locations += [v for v in vals if v not in locations]
    album = re.sub(r"\((Olympus Mjuii|Polariod|Polaroid|Nikon|B&W|colour)\)", "", name, flags=re.I)
    album = re.sub(r"^(NIkon|Nikon|Olympus|Zenit 11)\s*-\s*", "", album, flags=re.I)
    album = re.sub(r"\s+", " ", album.replace("_s", "'s")).strip()
    album = ALBUM_RENAMES.get(album, album)
    places = [dict(country=COUNTRIES.get(l, l), place=None if COUNTRIES.get(l) == l else l) for l in locations]
    return dict(album=album, camera=camera, year=int(year.group()) if year else None,
                location=places, bw=bool(re.search(r"\(B&W\)", name, re.I)))


# ---- Image helpers -------------------------------------------------------------
def dominant_colour(im):
    sm = im.copy(); sm.thumbnail((60, 60)); px = list(sm.getdata()); n = len(px)
    buckets, acc, colourful = {}, {}, 0
    for r, g, b in px:
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
        if s > 0.18 and 0.1 < l < 0.9:
            colourful += 1; d = h * 360
            k = ("red" if d < 18 or d >= 335 else "orange" if d < 42 else "yellow" if d < 68
                 else "green" if d < 160 else "blue" if d < 250 else "purple")
            buckets[k] = buckets.get(k, 0) + s * (1 - abs(l - .5) * 1.4)
            a = acc.setdefault(k, [0, 0, 0, 0]); a[0] += r; a[1] += g; a[2] += b; a[3] += 1
    if colourful / n < 0.06:
        a = [sum(p[i] for p in px) for i in range(3)] + [n]; colour = "mono"
    else:
        colour = max(buckets, key=buckets.get); a = acc[colour]
    return colour, "#%02x%02x%02x" % tuple(v // a[3] for v in a[:3])


def dhash(im):
    g = im.convert("L").resize((9, 8)); px = list(g.getdata())
    return sum(1 << i for i in range(64) if px[(i // 8) * 9 + i % 8] > px[(i // 8) * 9 + i % 8 + 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--carry-over", type=Path, help="older _shots-review.json to reuse decisions from")
    args = ap.parse_args()

    review = json.loads(REVIEW.read_text()) if REVIEW.exists() else {}
    old = json.loads(args.carry_over.read_text()) if args.carry_over and args.carry_over.exists() else {}
    OUT.mkdir(parents=True, exist_ok=True)

    # Originals before "name(1).jpg"-style copies, so the original is the one kept
    copy_suffix = re.compile(r"\s*\(\d+\)$")
    files = sorted((p for p in LIBRARY.rglob("*") if p.suffix.lower() in (".jpg", ".jpeg") and p.is_file()),
                   key=lambda p: (str(p.parent), copy_suffix.sub("", p.stem), bool(copy_suffix.search(p.stem))))
    photos, seen_hash, seen_sha, carried, dupes, skipped = [], {}, set(), 0, 0, 0
    for r in review.values():  # duplicates are worked out fresh each run, never stored
        if r.pop("duplicate", False): r["hidden"] = False
    for i, path in enumerate(files):
        rel = path.relative_to(LIBRARY).as_posix()
        if SKIP_FOLDERS.search(rel):
            skipped += 1; continue
        try:
            sha = hashlib.sha1(path.read_bytes()).hexdigest(); pid = sha[:10]
        except FileNotFoundError:  # moved or renamed while running
            skipped += 1; continue
        if sha in seen_sha:  # exact copy of a file already processed
            dupes += 1; continue
        seen_sha.add(sha)
        parts = rel.split("/")
        meta = parse_folder(parts[0])
        bw = meta["bw"] or any(BW_FOLDER.match(p.strip()) for p in parts[1:-1])

        r = review.get(sha)
        if r is None and sha in old:
            r = {k: v for k, v in old[sha].items() if k in ("rotate", "types", "hidden", "status")}; carried += 1
        r = r or {"rotate": 0, "types": [], "hidden": False, "status": "new"}
        r["path"] = rel; review[sha] = r

        im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        if r.get("rotate"):
            im = im.rotate(-r["rotate"], expand=True)
        for size, suffix, q in ((2000, "l", 82), (800, "s", 78)):
            fn = OUT / f"{pid}-{suffix}.jpg"
            if not fn.exists() or r.get("_rerender"):
                c = im.copy(); c.thumbnail((size, size), Image.LANCZOS)
                c.save(fn, "JPEG", quality=q, optimize=True, progressive=True)
        r.pop("_rerender", None)

        # Near-identical frames within the same album are accidental duplicates
        h = dhash(im); key = parts[0]
        # ...including copies scanned at a different rotation (labs sometimes deliver both)
        variants = [h] + [dhash(im.rotate(a, expand=True)) for a in (90, 180, 270)]
        if any(bin(v ^ h2).count("1") <= 3 for v in variants for h2 in seen_hash.get(key, [])):
            dupes += 1; r["rotated_copy"] = True; continue
        r.pop("rotated_copy", None)
        seen_hash.setdefault(key, []).append(h)

        if r.get("hidden"):
            continue
        colour, tint = dominant_colour(im)
        photos.append(dict(
            id=pid, title=meta["album"], album=meta["album"], location=meta["location"],
            camera=meta["camera"], year=meta["year"], colour="mono" if bw else colour, tint=tint,
            w=im.width, h=im.height, types=r.get("types", []), status=r.get("status"),
            src=dict(s=f"photos/{pid}-s.jpg", l=f"photos/{pid}-l.jpg")))
        if i % 100 == 0:
            print(f"{i}/{len(files)}", flush=True)

    # Stable, varied order: shuffle by id so the grid mixes trips
    photos.sort(key=lambda p: hashlib.md5(p["id"].encode()).hexdigest())
    REVIEW.write_text(json.dumps(review, indent=1))
    (OUT / "_data.js").write_text(
        "// GENERATED by tools/process_photos.py from design/photos (gitignored).\n"
        f"window.SHOTS_PHOTOGRAPHER = {json.dumps(PHOTOGRAPHER)};\n"
        "window.SHOTS_PHOTOS = " + json.dumps(photos, separators=(",", ":")) + ";\n")
    print(f"done: {len(photos)} photos, {carried} carried over, {dupes} duplicates hidden, {skipped} skipped")


if __name__ == "__main__":
    main()
