# -*- coding: utf-8 -*-
"""Select and copy work images from artist/*/작품 이미지 to images/artists/{slug}/"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIST_ROOT = ROOT / "artist"
OUT_ROOT = ROOT / "images" / "artists"
JSON_PATH = ROOT / "data" / "artists.json"

# Map folder name (as on disk) -> slug
ARTISTS = [
    ("강민성", "kang-minseong"),
    ("제시카 위", "jessica-wee"),
    ("진환민", "jin-hwanmin"),
    ("허승희", "heo-seunghee"),
]

IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG", ".PNG", ".WEBP"}
SKIP_NAME_PARTS = ("확정목록", "catalog", "Catalog", "리스트", "pptx")


def find_works_dir(artist_dir: Path) -> Path | None:
    for child in artist_dir.iterdir():
        if not child.is_dir():
            continue
        name = child.name
        if "작품" in name or name.lower() == "works":
            return child
    return None


def list_work_images(works_dir: Path) -> list[Path]:
    files: list[Path] = []
    for p in sorted(works_dir.iterdir()):
        if p.is_dir():
            # skip nested undecided folders for v1
            continue
        if p.suffix not in IMG_EXT:
            continue
        if any(s.lower() in p.name.lower() for s in SKIP_NAME_PARTS if s.isascii()):
            continue
        if "확정목록" in p.name:
            continue
        files.append(p)
    return files


def parse_meta(filename: str) -> dict:
    stem = Path(filename).stem
    year = ""
    m = re.search(r"(20\d{2})", stem)
    if m:
        year = m.group(1)

    medium = ""
    for key in ("Ceramic", "Glass", "Silver", "Oil", "Canvas", "mixed media", "리넨", "동양화물감"):
        if key.lower() in stem.lower() or key in stem:
            medium = (medium + ", " if medium else "") + key

    size = ""
    sm = re.search(r"(\d+[xX×_]\d+(?:[xX×_]\d+)?)\s*\(?\s*cm", stem, re.I)
    if sm:
        size = sm.group(1).replace("_", "x") + "cm"
    else:
        sm2 = re.search(r"(\d+)\s*[xX×]\s*(\d+)(?:\s*[xX×]\s*(\d+))?\s*cm", stem, re.I)
        if sm2:
            parts = [sm2.group(1), sm2.group(2)] + ([sm2.group(3)] if sm2.group(3) else [])
            size = "x".join(parts) + "cm"

    # title: take text before first comma or medium keyword
    title = stem
    for sep in [",", " Ceramic", " ceramic", " Oil", " mixed", "_", " 리넨"]:
        if sep in title:
            title = title.split(sep)[0]
            break
    title = re.sub(r"^\d+[\.\-\s]+", "", title).strip()
    title = re.sub(r"\s+", " ", title)
    if not title:
        title = stem

    return {"title": title, "year": year, "medium": medium, "size": size}


def copy_ext(src: Path) -> str:
    ext = src.suffix.lower()
    if ext == ".jpeg":
        return ".jpg"
    return ext


def main() -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    by_slug = {a["slug"]: a for a in data["artists"]}

    summary = []

    for folder_name, slug in ARTISTS:
        artist_dir = ARTIST_ROOT / folder_name
        if not artist_dir.is_dir():
            raise SystemExit(f"missing artist dir: {artist_dir}")

        works_dir = find_works_dir(artist_dir)
        if not works_dir:
            raise SystemExit(f"no works dir under {artist_dir}")

        images = list_work_images(works_dir)
        if not images:
            raise SystemExit(f"no images in {works_dir}")

        # Cap: hero + up to 5 more works (6 total max)
        selected = images[:6]

        out_dir = OUT_ROOT / slug
        works_out = out_dir / "works"
        promo_out = out_dir / "promo"
        works_out.mkdir(parents=True, exist_ok=True)
        promo_out.mkdir(parents=True, exist_ok=True)

        # Clear previous copies in works/promo/hero only
        for old in out_dir.glob("hero.*"):
            old.unlink()
        for old in works_out.iterdir():
            if old.is_file():
                old.unlink()

        hero_src = selected[0]
        hero_ext = copy_ext(hero_src)
        hero_dst = out_dir / f"hero{hero_ext}"
        shutil.copy2(hero_src, hero_dst)

        works_meta = []
        for i, src in enumerate(selected, start=1):
            ext = copy_ext(src)
            dst = works_out / f"{i:02d}{ext}"
            shutil.copy2(src, dst)
            meta = parse_meta(src.name)
            meta["image"] = f"images/artists/{slug}/works/{dst.name}"
            works_meta.append(meta)

        artist = by_slug[slug]
        artist["heroImage"] = f"images/artists/{slug}/{hero_dst.name}"
        artist["works"] = works_meta
        # promo left empty for now (user said works-only selection)
        artist["promo"] = artist.get("promo") or []

        summary.append(
            {
                "slug": slug,
                "source": str(works_dir.relative_to(ROOT)),
                "count": len(selected),
                "hero": hero_src.name,
                "files": [s.name for s in selected],
            }
        )

    JSON_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # verify
    missing = []
    for a in data["artists"]:
        for p in [a["heroImage"], *[w["image"] for w in a["works"]], *[p["image"] for p in a.get("promo", [])]]:
            if p and not (ROOT / p).exists():
                missing.append(p)
    if missing:
        raise SystemExit("missing:\n" + "\n".join(missing))

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(
        "OK",
        [
            {"slug": a["slug"], "works": len(a["works"]), "promo": len(a.get("promo", []))}
            for a in data["artists"]
        ],
    )


if __name__ == "__main__":
    main()
