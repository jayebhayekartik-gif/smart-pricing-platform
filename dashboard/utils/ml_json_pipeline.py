# dashboard/utils/ml_json_pipeline.py

import re
import json
import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

from xgboost import XGBRegressor
import lightgbm as lgb


# ------------------------------------------------------------
# SAFE NUMBER PARSER
# ------------------------------------------------------------
def safe_float(x):
    if x is None:
        return None
    x = str(x).replace(",", "")
    match = re.findall(r"-?\d+\.?\d*", x)
    return float(match[0]) if match else None


# ------------------------------------------------------------
# CLEAN THE SCRAPED JSON ARRAY
# (scraped_data.data[]  --> flattened ML dataset)
# ------------------------------------------------------------
def preprocess_scraped_json(json_array):
    """
    json_array = scraped_data.data (which is ALWAYS a list)
    Each item may contain:
        price, competitor_price, product_name, attributes...
    """

    if not isinstance(json_array, list):
        return pd.DataFrame()

    df = pd.json_normalize(json_array)

    if df.empty:
        return df

    # Extract numeric price column
    price_cols = [c for c in df.columns if "price" in c.lower()]

    # Find the best price column
    if "price" in df.columns:
        price_col = "price"
    elif "your_price" in df.columns:
        price_col = "your_price"
    elif price_cols:
        price_col = price_cols[0]
    else:
        return pd.DataFrame()

    df["price_numeric"] = df[price_col].apply(safe_float)

    # Convert all fields containing numbers
    for col in df.columns:
        if any(x in col.lower() for x in ["price", "qty", "amount", "value", "weight"]):
            df[col + "_num"] = df[col].apply(safe_float)

    # Encode text columns
    for col in df.columns:
        if df[col].dtype == "object":
            df[col + "_enc"] = df[col].astype(str).astype("category").cat.codes

    df = df.dropna(subset=["price_numeric"])
    df = df.reset_index(drop=True)

    return df


# ------------------------------------------------------------
# ML MODELS
# ------------------------------------------------------------
def train_xgb(X, y):
    model = XGBRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.8
    )
    model.fit(X, y)
    return model


def train_lgb(X, y):
    model = lgb.LGBMRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05
    )
    model.fit(X, y)
    return model


# ------------------------------------------------------------
# MAIN PIPELINE (for scraped_data.data[])
# ------------------------------------------------------------
def run_pipeline_json(scraped_json_array):
    """
    scraped_json_array = scraped_data["data"] (list of objects)

    RETURNS → final prediction JSON for model_outputs table:

    {
       "predicted_price": 102.55,
       "model_version": "xgb_lgb_v1",
       "confidence": 0.94
    }
    """

    df = preprocess_scraped_json(scraped_json_array)
    if df.empty:
        return None

    feature_cols = [c for c in df.columns if c.endswith("_num") or c.endswith("_enc")]

    X = df[feature_cols].fillna(0).values
    y = df["price_numeric"].values

    # XGB
    try:
        xgb = train_xgb(X, y)
        pred_xgb = xgb.predict(X)
    except:
        pred_xgb = np.full(len(df), np.nanmean(y))

    # LGB
    try:
        lgbm = train_lgb(X, y)
        pred_lgb = lgbm.predict(X)
    except:
        pred_lgb = np.full(len(df), np.nanmean(y))

    # Ensemble
    ensemble = np.nanmean(np.vstack([pred_xgb, pred_lgb]), axis=0)

    final_price = float(np.mean(ensemble))
    confidence = float(np.std(ensemble) / (abs(final_price) + 1e-6))  # simple uncertainty score

    trained_at = datetime.utcnow().isoformat() + "Z"

    # RETURN JSON for model_outputs table
    result = {
        "predicted_price": final_price,
        "model_version": "xgb_lgb_v1",
        "confidence": round(float(1 - confidence), 4),
        "trained_at": trained_at
    }

    return result




