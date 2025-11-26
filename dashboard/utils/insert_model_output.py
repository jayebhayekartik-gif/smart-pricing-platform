# dashboard/utils/insert_model_output.py

from dashboard.utils.supabase_client import get_supabase
from datetime import datetime

def upsert_model_output(
    product_uuid: str,
    model_name: str,
    prediction_json: dict,
    metadata_json: dict = None
):
    """
    Insert or update a model output row in the Supabase model_outputs table.

    IMPORTANT:
    New supabase-py client DOES NOT allow .select() after an UPSERT.
    So we only call .upsert().execute().
    """

    supabase = get_supabase()

    row = {
        "product_id": product_uuid,
        "model_name": model_name,
        "prediction": prediction_json,
        "metadata": metadata_json or {},
        "predicted_at": datetime.utcnow().isoformat() + "Z"
    }

    # FIXED: remove .select("*")
    result = (
        supabase.table("model_outputs")
        .upsert(row, on_conflict="product_id,model_name")
        .execute()
    )

    return result.data

