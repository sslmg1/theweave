# -*- coding: utf-8 -*-
"""Convert artist bio/*cv*.docx to PDF via Word COM (Windows)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIST_DIR = ROOT / "artist"
OUT_ROOT = ROOT / "files" / "artists"
JSON_PATH = ROOT / "data" / "artists.json"

FOLDER_TO_SLUG = {
    "강민성": "kang-minseong",
    "제시카 위": "jessica-wee",
    "진환민": "jin-hwanmin",
    "허승희": "heo-seunghee",
}

DOWNLOAD_NAMES = {
    "kang-minseong": "강민성_CV.pdf",
    "jessica-wee": "Jessica_Wee_CV.pdf",
    "jin-hwanmin": "진환민_CV.pdf",
    "heo-seunghee": "허승희_CV.pdf",
}


def find_cv_docx(bio_dir: Path) -> Path | None:
    candidates = []
    for f in bio_dir.iterdir():
        if f.suffix.lower() != ".docx":
            continue
        name = f.name.lower()
        if "cv" not in name:
            continue
        if any(x in name for x in ("소개", "statement", "bio")):
            continue
        candidates.append(f)
    return candidates[0] if candidates else None


def convert_with_word(pairs: list[tuple[Path, Path]]) -> None:
    # Build a PowerShell script with UTF-8 BOM so Korean paths work.
    lines = [
        "$ErrorActionPreference = 'Stop'",
        "$wdFormatPDF = 17",
        "$word = New-Object -ComObject Word.Application",
        "$word.Visible = $false",
        "$word.DisplayAlerts = 0",
        "try {",
    ]
    for src, dst in pairs:
        src_s = str(src).replace("'", "''")
        dst_s = str(dst).replace("'", "''")
        lines += [
            f"  Write-Host 'Converting: {src.name}'",
            f"  $src = '{src_s}'",
            f"  $dst = '{dst_s}'",
            "  if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Force }",
            "  $doc = $word.Documents.Open($src, $false, $true)",
            "  try { $doc.SaveAs([ref]$dst, [ref]$wdFormatPDF) } finally { $doc.Close($false) }",
            "  if (Test-Path -LiteralPath $dst) { Write-Host ('  OK ' + (Get-Item -LiteralPath $dst).Length) }",
            "  else { throw \"PDF missing: $dst\" }",
        ]
    lines += [
        "} finally {",
        "  $word.Quit()",
        "  [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null",
        "}",
        "Write-Host 'Done.'",
    ]

    ps1 = ROOT / "scripts" / "_tmp_convert_cv.ps1"
    ps1.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
    try:
        proc = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ps1),
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        sys.stdout.write(proc.stdout or "")
        sys.stderr.write(proc.stderr or "")
        if proc.returncode != 0:
            raise SystemExit(f"Word conversion failed (exit {proc.returncode})")
    finally:
        if ps1.exists():
            ps1.unlink()


def update_json(cv_paths: dict[str, str]) -> None:
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    for artist in data.get("artists", []):
        slug = artist.get("slug") or artist.get("id")
        if slug in cv_paths:
            artist["cvPdf"] = cv_paths[slug]
    JSON_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"updated {JSON_PATH}")


def main() -> None:
    pairs: list[tuple[Path, Path]] = []
    cv_paths: dict[str, str] = {}

    for folder_name, slug in FOLDER_TO_SLUG.items():
        bio = ARTIST_DIR / folder_name / "bio"
        if not bio.is_dir():
            print(f"skip missing bio: {bio}")
            continue
        docx = find_cv_docx(bio)
        if not docx:
            print(f"skip no cv docx: {bio}")
            continue
        out_dir = OUT_ROOT / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        pdf_name = DOWNLOAD_NAMES[slug]
        pdf_path = out_dir / pdf_name
        pairs.append((docx, pdf_path))
        cv_paths[slug] = f"files/artists/{slug}/{pdf_name}"

    if not pairs:
        raise SystemExit("No CV docx files found")

    convert_with_word(pairs)
    update_json(cv_paths)
    print("CV PDFs ready:")
    for slug, rel in cv_paths.items():
        p = ROOT / rel
        print(f"  {slug}: {rel} ({p.stat().st_size if p.exists() else 'MISSING'} bytes)")


if __name__ == "__main__":
    main()
