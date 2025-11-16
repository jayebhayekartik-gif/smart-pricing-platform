# api/ml_pipeline.py

"""
This file is a LIGHTWEIGHT WRAPPER that calls the REAL ML model
from your dashboard utils (ml_json_pipeline.py).

Do NOT put ML logic inside this file.
"""

import json
from dashboard.utils.ml_json_pipeline import run_pipeline_json


def run_ml_on_scraped(scraped_list):
    """
    scraped_list → array of JSON objects from scraped_data.data

    Example:
    [
      {"price": "₹ 105", "supplier": "A", "qty": "30 kg"},
      {"price": "₹ 110", "supplier": "B", "qty": "25 kg"}
    ]

    Returns:
      A SINGLE final prediction JSON (dict), like:

      {
        "predicted_price": 104.52,
        "model_version": "xgb_lgb_v1",
        "confidence": 0.91,
        "trained_at": "2025-11-15T12:20:31Z"
      }
    """

    # Use your existing ML model
    result = run_pipeline_json(scraped_list)

    # Pipeline returns either:
    # - dict  → expected (correct)
    # - None  → if no valid training data
    return result
