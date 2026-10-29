"""Protect existing research and annotation outputs."""
from pathlib import Path

def refuse_existing(paths):
    existing = [str(p) for p in paths if Path(p).exists()]
    if existing:
        raise FileExistsError("Refusing to overwrite existing outputs: " + ", ".join(existing) +
                              ". Run template generation in a separate working copy.")
