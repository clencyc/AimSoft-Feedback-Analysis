from functools import lru_cache
from typing import Dict
import importlib

# Ensure torch is available and visible to the transformers.pipelines module.
# Some transformers versions expect a global `torch` name in that module and
# will raise NameError if it's missing even when torch isn't required at import time.
try:
    import torch
except Exception as exc:
    raise RuntimeError(
        "PyTorch is required for the sentiment pipeline. Install the CPU build (see backend/requirements.txt) and restart the server."
    ) from exc

try:
    import transformers.pipelines as _tp
    _tp.torch = torch
except Exception:
    # non-fatal: if we cannot inject, proceed and let pipeline raise a clear error
    pass

from transformers import pipeline


@lru_cache(maxsize=1)
def get_sentiment_pipeline():
    """Return a cached HF sentiment-analysis pipeline.

    The pipeline is loaded once per process (per Gunicorn worker) thanks to
    lru_cache(maxsize=1).
    """
    return pipeline(
        "sentiment-analysis",
        model="distilbert-base-uncased-finetuned-sst-2-english",
    )


def analyze_sentiment(text: str) -> Dict:
    """Analyze text and return a normalized result dict.

    Returns: {"label": str, "score": float} with score rounded to 4 decimals.
    """
    pipe = get_sentiment_pipeline()
    result = pipe(text, truncation=True)[0]
    return {"label": result.get("label"), "score": round(float(result.get("score", 0.0)), 4)}
