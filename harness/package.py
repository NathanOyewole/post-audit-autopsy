"""Package the eval into a submission ZIP (code only, <= 50 MB)."""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist"
OUT.mkdir(exist_ok=True)

INCLUDE_DIRS = ["harness", "tasks", "docs"]
INCLUDE_FILES = ["README.md"]
EXCLUDE = {"__pycache__", ".git", "external", "dist", "results"}


def main():
    zip_path = OUT / "post-audit-autopsy.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for d in INCLUDE_DIRS:
            for f in (ROOT / d).rglob("*"):
                if any(part in EXCLUDE for part in f.parts):
                    continue
                if f.is_file():
                    z.write(f, f.relative_to(ROOT))
        for f in INCLUDE_FILES:
            p = ROOT / f
            if p.exists():
                z.write(p, p.relative_to(ROOT))
        # include results summary if present
        summary = ROOT / "results" / "summary.json"
        if summary.exists():
            z.write(summary, "results/summary.json")
    size = zip_path.stat().st_size / 1024 / 1024
    print(f"wrote {zip_path} ({size:.2f} MB)")


if __name__ == "__main__":
    main()
