# -*- coding: utf-8 -*-
"""Convert project images/ to WebP (max width 2000px). Move originals outside repo."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGES = ROOT / "images"
BACKUP = ROOT.parent / "originals_backup"
MAX_WIDTH = 2000
QUALITY = 82
EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".JPG", ".JPEG", ".PNG", ".GIF", ".WEBP"}


def collect_images() -> list[Path]:
    files: list[Path] = []
    if not IMAGES.exists():
        return files
    for p in IMAGES.rglob("*"):
        if p.is_file() and p.suffix in EXTS:
            files.append(p)
    return sorted(files)


def to_webp_path(src: Path) -> Path:
    return src.with_suffix(".webp")


def convert_one(src: Path) -> Path:
    """Write webp next to src (or replace if already webp), move original to backup. Return new path."""
    rel = src.relative_to(ROOT)
    backup_path = BACKUP / rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    dest = to_webp_path(src)
    # Avoid clobbering if converting foo.webp -> foo.webp in place via temp
    tmp = src.with_name(src.stem + ".__tmp__.webp")

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
        if im.mode == "RGBA":
            # WebP supports alpha
            im.save(tmp, "WEBP", **save_kwargs)
        else:
            im.convert("RGB").save(tmp, "WEBP", **save_kwargs)

    # Move original to backup (if backup exists, replace)
    if backup_path.exists():
        backup_path.unlink()
    shutil.move(str(src), str(backup_path))

    # Place final webp at dest
    if dest.exists() and dest != tmp:
        dest.unlink()
    if tmp != dest:
        tmp.replace(dest)
    else:
        # src was already .webp path and we moved it; tmp is the new file
        pass

    # If src was foo.webp, we moved it to backup and tmp is foo.__tmp__.webp -> rename to foo.webp
    if dest.name.endswith(".__tmp__.webp"):
        final = dest.with_name(src.stem.replace(".__tmp__", "") + ".webp")
        # shouldn't happen
    if tmp.exists():
        final = src.with_suffix(".webp") if src.suffix.lower() != ".webp" else src
        # After move, src path is free
        if final.exists() and final != tmp:
            final.unlink()
        shutil.move(str(tmp), str(final))
        return final

    return dest if dest.exists() else src.with_suffix(".webp")


def convert_one_fixed(src: Path) -> tuple[Path, Path]:
    """Convert image to WebP, backup original. Returns (new_path, backup_path)."""
    rel = src.relative_to(ROOT)
    backup_path = BACKUP / rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)

    new_path = src.with_suffix(".webp")
    tmp = src.parent / (src.stem + ".__conv__.webp")

    with Image.open(src) as im:
        has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
        if has_alpha:
            im = im.convert("RGBA")
        else:
            im = im.convert("RGB")

        w, h = im.size
        if w > MAX_WIDTH:
            nh = max(1, int(round(h * (MAX_WIDTH / float(w)))))
            im = im.resize((MAX_WIDTH, nh), Image.Resampling.LANCZOS)

        im.save(tmp, "WEBP", quality=QUALITY, method=6)

    # Backup original
    if backup_path.exists():
        backup_path.unlink()
    shutil.move(str(src), str(backup_path))

    # If converting webp->webp, new_path may equal old src path (now free)
    if new_path.exists() and new_path.resolve() != tmp.resolve():
        new_path.unlink()
    shutil.move(str(tmp), str(new_path))
    return new_path, backup_path


def replace_paths_in_text(text: str, mapping: dict[str, str]) -> str:
    out = text
    # Longer keys first to avoid partial replaces
    for old, new in sorted(mapping.items(), key=lambda kv: len(kv[0]), reverse=True):
        out = out.replace(old, new)
        out = out.replace(old.replace("\\", "/"), new)
    return out


def update_code_refs(mapping: dict[str, str]) -> list[str]:
    changed: list[str] = []
    targets = [
        ROOT / "data" / "artists.json",
        ROOT / "services.html",
        ROOT / "css" / "style.css",
        ROOT / "index.html",
        ROOT / "about.html",
        ROOT / "contact.html",
        ROOT / "artists.html",
        ROOT / "artist.html",
        ROOT / "magazine-article.html",
        ROOT / "index_t.html",
        ROOT / "js" / "artists.js",
        ROOT / "js" / "main.js",
    ]
    for path in targets:
        if not path.exists():
            continue
        raw = path.read_text(encoding="utf-8")
        updated = replace_paths_in_text(raw, mapping)
        if updated != raw:
            path.write_text(updated, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    return changed


def dir_size(path: Path) -> int:
    total = 0
    if not path.exists():
        return 0
    for p in path.rglob("*"):
        if p.is_file():
            total += p.stat().st_size
    return total


def fmt_bytes(n: int) -> str:
    mb = n / (1024 * 1024)
    if mb >= 1:
        return f"{mb:.2f} MB ({n:,} bytes)"
    kb = n / 1024
    return f"{kb:.1f} KB ({n:,} bytes)"


def main() -> None:
    files = collect_images()
    print(f"found {len(files)} images under images/")
    BACKUP.mkdir(parents=True, exist_ok=True)

    mapping: dict[str, str] = {}
    results = []

    for src in files:
        # Skip temp files
        if ".__conv__" in src.name or ".__tmp__" in src.name:
            continue
        old_rel = src.relative_to(ROOT).as_posix()
        try:
            new_path, backup_path = convert_one_fixed(src)
            new_rel = new_path.relative_to(ROOT).as_posix()
            mapping[old_rel] = new_rel
            results.append(
                {
                    "from": old_rel,
                    "to": new_rel,
                    "backup": str(backup_path),
                    "size": new_path.stat().st_size,
                }
            )
            print(f"OK  {old_rel} -> {new_rel}")
        except Exception as e:
            print(f"ERR {old_rel}: {e}")
            raise

    changed = update_code_refs(mapping)
    print("code updated:", changed)

    # artists.json promo paths if any leftover
    artists_path = ROOT / "data" / "artists.json"
    if artists_path.exists():
        data = json.loads(artists_path.read_text(encoding="utf-8"))
        # ensure any remaining non-webp under images/artists get fixed via mapping already
        artists_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    total = dir_size(IMAGES)
    print("SUMMARY")
    print(f"converted: {len(results)}")
    print(f"images/ size: {fmt_bytes(total)}")
    print(f"backup: {BACKUP}")


if __name__ == "__main__":
    main()
