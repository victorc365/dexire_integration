import pathlib
import os

DATASETS_DIR = pathlib.Path(__file__).parent / "data"
CACHE_DIR = pathlib.Path(__file__).parent / "cache"

if not os.path.exists(CACHE_DIR / "interactive"):
    os.mkdir(CACHE_DIR / "interactive")