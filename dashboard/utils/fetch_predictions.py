# dashboard/utils/fetch_predictions.py

from dashboard.utils.supabase_client import get_supabase


# -----------------------------------------------------------
# Fetch the LATEST prediction for a product (any model)
# -----------------------------------------------------------
def fetch_latest_prediction(product_uuid: str):
    """
    Returns the most recent model_outputs row for a product.
    Useful for dashboard display of the newest ML prediction.
    """

    supabase = get_supabase()

    res = (
        supabase
        .table("model_outputs")
        .select("*")
        .eq("product_id", product_uuid)
        .order("predicted_at", desc=True)
        .limit(1)
        .execute()
    )

    if not res.data:
        return None

    return res.data[0]


# -----------------------------------------------------------
# Fetch ALL model outputs for a product
# -----------------------------------------------------------
def fetch_all_predictions(product_uuid: str):
    """
    Returns every model prediction row for this product.
    Useful for analytics or comparison pages.
    """

    supabase = get_supabase()

    res = (
        supabase
        .table("model_outputs")
        .select("*")
        .eq("product_id", product_uuid)
        .order("predicted_at", desc=False)
        .execute()
    )

    return res.data if res.data else []


# -----------------------------------------------------------
# Fetch prediction for a specific model_name
# -----------------------------------------------------------
def fetch_prediction_by_model(product_uuid: str, model_name: str):
    """
    Returns ONE row: prediction for a specific model from model_outputs.
    """

    supabase = get_supabase()

    res = (
        supabase
        .table("model_outputs")
        .select("*")
        .eq("product_id", product_uuid)
        .eq("model_name", model_name)
        .limit(1)
        .execute()
    )

    if not res.data:
        return None

    return res.data[0]


# -----------------------------------------------------------
# Testing
# -----------------------------------------------------------
if __name__ == "__main__":
    TEST_UUID = "REPLACE-WITH-UUID"

    print("LATEST PREDICTION:", fetch_latest_prediction(TEST_UUID))
    print("ALL PREDICTIONS:", fetch_all_predictions(TEST_UUID))
    print("XGB MODEL:", fetch_prediction_by_model(TEST_UUID, "pricing_model_v1"))




