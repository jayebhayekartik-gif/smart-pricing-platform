from datetime import datetime
from .supabase_client import supabase

def upsert_model_output(product_uuid: str, model_name: str, prediction_json: dict, metadata=None):
    row = {
        "product_id": product_uuid,
        "model_name": model_name,
        "prediction": prediction_json,
        "metadata": metadata or {},
        "predicted_at": datetime.utcnow().isoformat() + "Z"
    }

    # NEW SCHEMA → UNIQUE(product_id, model_name)
    res = (
        supabase.table("model_outputs")
        .upsert(row, on_conflict="product_id,model_name")
        .select("*")
        .execute()
    )

    return res.data
