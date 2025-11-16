# dashboard/utils/product_selector.py

from dashboard.utils.supabase_client import get_supabase


# --------------------------------------------------------------
# Fetch ALL products (for sidebar dropdown)
# --------------------------------------------------------------
def fetch_all_products():
    """
    Returns a list of all products:
    [
      {
        "id": "...uuid...",
        "product_id": "ABC001",
        "name": "PP Granules",
        "your_price": 72.5,
        "domain": "india",
        "timestamp": "...",
      }
    ]
    """
    supabase = get_supabase()
    
    res = (
        supabase
        .table("products")
        .select("*")
        .order("name", desc=False)
        .execute()
    )

    return res.data if res.data else []


# --------------------------------------------------------------
# Fetch SINGLE product using UUID
# --------------------------------------------------------------
def get_product_by_uuid(product_uuid: str):
    """
    Fetch full product row for dashboard header.
    """
    supabase = get_supabase()

    res = (
        supabase
        .table("products")
        .select("*")
        .eq("id", product_uuid)
        .limit(1)
        .execute()
    )

    if not res.data:
        return None
    
    return res.data[0]


# --------------------------------------------------------------
# Get product UUID using any combination of:
#   - name
#   - product_id
#   - domain
# --------------------------------------------------------------
def find_product_uuid(name: str = None, product_id: str = None, domain: str = None):
    """
    Example:
        find_product_uuid(name="PP Granules", product_id="ABC001", domain="india")
    """

    supabase = get_supabase()

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


# --------------------------------------------------------------
# Testing
# --------------------------------------------------------------
if __name__ == "__main__":
    # Fetch all products
    print("All Products:", fetch_all_products())

    # Try finding a specific product
    uuid = find_product_uuid(product_id="ABC001", domain="india")
    print("Found UUID:", uuid)

    if uuid:
        print("Product Details:", get_product_by_uuid(uuid))


