# -*- coding: utf-8 -*-
"""Sync all artist works from artist/*/works into images/artists/*/works + artists.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "data" / "artists.json"
MAX_WIDTH = 2000
QUALITY = 82
IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff"}

FOLDER_TO_SLUG = {
    "강민성": "kang-minseong",
    "제시카 위": "jessica-wee",
    "진환민": "jin-hwanmin",
    "허승희": "heo-seunghee",
}


def nfkc(s: str) -> str:
    import unicodedata

    return unicodedata.normalize("NFKC", s)


def list_source_images(works_dir: Path) -> list[Path]:
    # Include nested folders (e.g. works/미정)
    files = [
        p
        for p in works_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in IMG_EXTS
    ]
    return sorted(files, key=sort_key)


def sort_key(p: Path):
    name = nfkc(p.name)
    # Heo-style: "1. title..."
    m = re.match(r"^(\d+)\.", name)
    if m:
        return (0, int(m.group(1)), name.lower())
    # Jin-style: "12-SNA..." or "2-DSCF..."
    m = re.match(r"^(\d+)-", name)
    if m:
        return (1, int(m.group(1)), name.lower())
    # Leading bare number file like 100호
    m = re.match(r"^(\d+)", name)
    if m and not name.lower().startswith("kakao"):
        return (2, int(m.group(1)), name.lower())
    return (3, 0, name.lower())


def parse_meta(path: Path) -> dict:
    stem = nfkc(path.stem)
    title = stem
    year = ""
    medium = ""
    size = ""

    # Heo: "1. 고결 Nobleness, 리넨에 동양화물감, 금, 120x120cm, 2025"
    m = re.match(r"^\d+\.\s*(.+)$", stem)
    if m:
        parts = [p.strip() for p in m.group(1).split(",")]
        title = parts[0] if parts else stem
        for p in parts[1:]:
            if re.fullmatch(r"\d{4}", p):
                year = p
            elif re.search(r"\d+\s*[x×X]\s*\d+", p, re.I):
                size = re.sub(r"\s+", "", p)
            elif not medium:
                medium = p
            else:
                medium = f"{medium}, {p}"
        return {"title": title, "year": year, "medium": medium, "size": size}

    # Kang / Breath-in style with commas and year
    # "Breath in_ N26101,  ceramic, 25X25X26cm(h) 2026"
    year_m = re.search(r"(19|20)\d{2}\s*$", stem)
    if year_m:
        year = year_m.group(0).strip()
        stem_wo = stem[: year_m.start()].rstrip(" ,_-")
    else:
        stem_wo = stem

    size_m = re.search(
        r"(\d+\s*[x×X_]\s*\d+(?:\s*[x×X_]\s*\d+)?\s*(?:\(cm\)|cm)?(?:\(h\))?)",
        stem_wo,
        re.I,
    )
    if size_m:
        size = (
            size_m.group(1)
            .replace("_", "x")
            .replace("×", "x")
            .replace(" ", "")
        )
        size = re.sub(r"\(cm\)", "cm", size, flags=re.I)

    # Jessica / simple underscore titles
    if "_" in stem_wo and "," not in stem_wo:
        base = stem_wo.split("_")[0].strip()
        # Wee_Work2_Shelf Portrait1...
        if stem_wo.lower().startswith("wee_work"):
            rest = re.sub(r"^Wee_Work\d+_", "", stem_wo, flags=re.I)
            rest = re.sub(r"_Credit_.*$", "", rest, flags=re.I).replace("_", " ").strip()
            title = rest or "Wee"
        elif stem_wo.lower().startswith("04_bojagi"):
            title = "Bojagi Revealing"
            year_m2 = re.search(r"(20\d{2})", stem_wo)
            if year_m2:
                year = year_m2.group(1)
            medium_m = re.search(r"Oil_on_Canvas", stem_wo, re.I)
            if medium_m:
                medium = "Oil on Canvas"
            size_m2 = re.search(r"(\d+x\d+in)", stem_wo, re.I)
            if size_m2:
                size = size_m2.group(1)
        else:
            title = base
        # clean credit suffixes already handled
        title = re.sub(r"_Credit_.*$", "", title, flags=re.I)
        return {"title": title, "year": year, "medium": medium, "size": size}

    # Jin SNA files: "12-SNA03117" or "SNA03117"
    m = re.search(r"(SNA\d+)", stem_wo, re.I)
    if m:
        return {"title": m.group(1).upper(), "year": year, "medium": medium, "size": size}

    # 100호
    if "100" in stem_wo and "호" in stem_wo:
        return {"title": "100호", "year": year, "medium": medium, "size": size}

    # KakaoTalk phone photos — keep short generic title from stem
    if stem_wo.lower().startswith("kakaotalk"):
        return {"title": "Work", "year": year, "medium": medium, "size": size}

    # Comma-separated metadata
    if "," in stem_wo:
        parts = [p.strip() for p in stem_wo.split(",")]
        title = parts[0]
        title = re.sub(r"_+\s*$", "", title).strip()
        for p in parts[1:]:
            if re.search(r"\d+\s*[x×X]\s*\d+", p, re.I):
                size = re.sub(r"\s+", "", p)
            elif p and not medium:
                medium = p.strip()
            elif p:
                medium = f"{medium}, {p.strip()}" if medium else p.strip()
        return {"title": title, "year": year, "medium": medium.strip(" ,"), "size": size}

    title = re.sub(r"_Credit_.*$", "", stem_wo, flags=re.I).replace("_", " ").strip()
    return {"title": title, "year": year, "medium": medium, "size": size}


def convert_to_webp(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        if im.mode in ("P", "RGBA", "LA"):
            im = im.convert("RGBA")
        elif im.mode != "RGB":
            im = im.convert("RGB")
        w, h = im.size
        if w > MAX_WIDTH:
            nh = int(round(h * (MAX_WIDTH / w)))
            im = im.resize((MAX_WIDTH, nh), Image.Resampling.LANCZOS)
        save_kwargs = {"quality": QUALITY, "method": 6}
        tmp = dest.with_suffix(".tmp.webp")
        if im.mode == "RGBA":
            im.save(tmp, "WEBP", **save_kwargs)
        else:
            im.convert("RGB").save(tmp, "WEBP", **save_kwargs)
        tmp.replace(dest)


def sync_artist(folder_name: str, slug: str) -> list[dict]:
    src_dir = ROOT / "artist" / folder_name / "works"
    out_dir = ROOT / "images" / "artists" / slug / "works"
    if not src_dir.is_dir():
        print(f"skip missing {src_dir}")
        return []

    # Clear existing webp works (rebuild clean numbering)
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("*.webp"):
        old.unlink()

    sources = list_source_images(src_dir)
    works = []
    for i, src in enumerate(sources, start=1):
        dest_name = f"{i:02d}.webp"
        dest = out_dir / dest_name
        print(f"  [{slug}] {src.name} -> {dest_name}")
        convert_to_webp(src, dest)
        meta = parse_meta(src)
        works.append(
            {
                "title": meta["title"],
                "year": meta["year"],
                "medium": meta["medium"],
                "size": meta["size"],
                "image": f"images/artists/{slug}/works/{dest_name}",
            }
        )
    return works


def main() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    by_slug = {a.get("slug") or a.get("id"): a for a in data["artists"]}

    for folder, slug in FOLDER_TO_SLUG.items():
        print(f"=== {folder} ({slug}) ===")
        works = sync_artist(folder, slug)
        if slug in by_slug:
            by_slug[slug]["works"] = works
            print(f"  -> {len(works)} works")

    JSON_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("updated", JSON_PATH)


if __name__ == "__main__":
    main()
