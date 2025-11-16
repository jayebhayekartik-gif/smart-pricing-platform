# dashboard/utils/scraped_data_access.py

from dashboard.utils.supabase_client import get_supabase

supabase = get_supabase()


# ----------------------------------------------------------
# 1. Fetch product UUID using (name, product_id, domain)
# ----------------------------------------------------------
def get_product_uuid(name: str = None, product_id: str = None, domain: str = None):
    q = supabase.table("products").select("id")

    if name:
        q = q.eq("name", name)
    if product_id:
        q = q.eq("product_id", product_id)
    if domain:
        q = q.eq("domain", domain)

    res = q.limit(1).execute()

    if not res.data:
        return None
    
    return res.data[0]["id"]


# ----------------------------------------------------------
# 2. Fetch full scraped_data row
# ----------------------------------------------------------
def fetch_scraped_data(product_uuid: str):
    res = (
        supabase
        .table("scraped_data")
        .select("*")
        .eq("product_id", product_uuid)
        .limit(1)
        .execute()
    )
    return res.data[0] if res.data else None


# ----------------------------------------------------------
# 3. Fetch JSON array only
# ----------------------------------------------------------
def fetch_scraped_json(product_uuid: str):
    res = (
        supabase
        .table("scraped_data")
        .select("data")
        .eq("product_id", product_uuid)
        .limit(1)
        .execute()
    )

    if not res.data:
        return []

    return res.data[0]["data"]  # always an array


# ----------------------------------------------------------
# Tests
# ----------------------------------------------------------
if __name__ == "__main__":
    uuid = get_product_uuid(product_id="ABC001", domain="india")

    print("PRODUCT UUID:", uuid)
    print("SCRAPED ROW:", fetch_scraped_data(uuid))
    print("SCRAPED JSON:", fetch_scraped_json(uuid))
