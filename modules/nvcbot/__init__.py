import pathlib
import os

DATASETS_DIR = pathlib.Path(__file__).parent / "data"
CACHE_DIR = pathlib.Path(__file__).parent / "cache"
DATASET = DATASETS_DIR / "df_final_7000_with_classes.csv"

if not os.path.exists(CACHE_DIR / "interactive"):
    os.mkdir(CACHE_DIR / "interactive")