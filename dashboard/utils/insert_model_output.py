# dashboard/utils/insert_model_output.py

from dashboard.utils.supabase_client import get_supabase
from datetime import datetime

supabase = get_supabase()


def upsert_model_output(
    product_uuid: str,
    model_name: str,
    prediction_json: dict,
    metadata_json: dict = None
):
    """
    Writeback ML predictions into Supabase.

    Schema enforces:
    - UNIQUE(product_id, model_name)
    - prediction: JSONB
    - metadata:  JSONB
    """

    row = {
        "product_id": product_uuid,
        "model_name": model_name,
        "prediction": prediction_json,
        "metadata": metadata_json or {},
        "predicted_at": datetime.utcnow().isoformat() + "Z"
    }

    res = (
        supabase
        .table("model_outputs")
        .upsert(row, on_conflict="product_id,model_name")
        .select("*")
        .execute()
    )

    return res.data


# Test
if __name__ == "__main__":
    uuid = "REPLACE_UUID"

    result = upsert_model_output(
        uuid,
        "xgb_model",
        {"predicted_price": 123.45, "confidence": 0.88},
        {"notes": "test run"}
    )

    print(result)
