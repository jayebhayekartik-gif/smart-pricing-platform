from datetime import datetime
from .supabase_client import supabase

def upsert_model_output(product_uuid: str, model_name: str, prediction_json: dict, metadata=None):
    row = {
        "product_id": product_uuid,
        "model_name": model_name,
        "prediction": prediction_json,
        "metadata": metadata,
        "predicted_at": datetime.utcnow().isoformat() + "Z"
    }

    res = (
        supabase.table("model_outputs")
        .upsert(row, on_conflict="product_id,model_name")
        .execute()
    )

    return res.data

