from pathlib import Path

import pandas as pd
from fastapi import HTTPException


_STATE_DIR = Path(__file__).resolve().parents[1] / ".state"
_DATASET_FILE = _STATE_DIR / "current_dataset.pkl"


def save_dataset(df: pd.DataFrame) -> None:
    _STATE_DIR.mkdir(parents=True, exist_ok=True)
    df.to_pickle(_DATASET_FILE)


def load_dataset() -> pd.DataFrame:
    if not _DATASET_FILE.exists():
        raise HTTPException(status_code=400, detail="No dataset uploaded")

    try:
        return pd.read_pickle(_DATASET_FILE)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Stored dataset is unreadable: {exc}") from exc
