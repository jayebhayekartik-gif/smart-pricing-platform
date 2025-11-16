from .supabase_client import supabase

def fetch_scraped_json(product_uuid: str):
    res = (
        supabase.table("scraped_data")
        .select("data")
        .eq("product_id", product_uuid)
        .limit(1)
        .execute()
    )

    if not res.data:
        return None

    return res.data[0]["data"]   # This is ALWAYS a JSON ARRAY
