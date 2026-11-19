#!/usr/bin/env python3
"""news-image-20261118 entry program.

The entry is the poster in entry.png beside this file (one day's world
news on a single page, drawn by compose.py). The harness grades exactly
the bytes of that image, so this program simply copies it to
$MAKEFUN_OUTPUT_DIR/entry.png (MAKEFUN_OUTPUT_DIR stands in for /output
outside the grader's container).
"""

import os
import shutil
from pathlib import Path


def main() -> None:
    source = Path(__file__).resolve().parent / "entry.png"
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, out_dir / "entry.png")


if __name__ == "__main__":
    main()
