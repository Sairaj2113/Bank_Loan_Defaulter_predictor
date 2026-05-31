from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

MODEL_PATH = Path(__file__).resolve().parents[3] / "models" / "LightGBM.pkl"


def load_model_bundle(path: Path | None = None) -> dict[str, Any]:
    model_path = Path(path) if path is not None else MODEL_PATH
    if not model_path.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {model_path}. Run `python training/train.py` first."
        )

    bundle = joblib.load(model_path)
    if isinstance(bundle, dict):
        return bundle

    return {"pipeline": bundle, "metadata": {}}

