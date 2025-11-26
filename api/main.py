from fastapi import FastAPI
from pydantic import BaseModel

from .supabase_client import supabase
from .scraped_data import fetch_scraped_json
from .ml_pipeline import run_ml_on_scraped
from .model_output import upsert_model_output


app = FastAPI(title="Smart Pricing Platform API")


# ------------------------------------------------------------------------------------
# 1️⃣ AUTO MODEL FOR A SPECIFIC PRODUCT (PATH PARAM — CLEAN & EASY)
# ------------------------------------------------------------------------------------
@app.post("/run-model/{product_uuid}")
def run_model_by_path(product_uuid: str):

    scraped = fetch_scraped_json(product_uuid)
    if not scraped:
        return {
            "status": "error",
            "message": f"No scraped_data found for product: {product_uuid}"
        }

    # Run ML
    prediction = run_ml_on_scraped(scraped)

    # Save
    saved = upsert_model_output(
        product_uuid,
        model_name="pricing_model_v1",
        prediction_json=prediction
    )

    return {
        "status": "success",
        "product_uuid": product_uuid,
        "prediction": prediction,
        "database_saved": saved
    }


# ------------------------------------------------------------------------------------
# 2️⃣ LIST ALL PRODUCTS AVAILABLE
# ------------------------------------------------------------------------------------
@app.get("/list-products")
def list_all_products():

    products = supabase.table("products").select("*").execute().data

    return {
        "status": "success",
        "count": len(products),
        "products": products
    }


# ------------------------------------------------------------------------------------
# 3️⃣ API STATUS CHECK
# ------------------------------------------------------------------------------------
@app.get("/status")
def status():
    return {
        "api": "Smart Pricing Platform API",
        "status": "running",
        "version": "1.0.0",
        "powered_by": "FastAPI + Supabase"
    }


# ------------------------------------------------------------------------------------
# 4️⃣ TRAIN ONLY PRODUCTS IN SPECIFIC DOMAIN (example: india)
# ------------------------------------------------------------------------------------
@app.post("/force-train/{domain}")
def train_by_domain(domain: str):

    # Fetch all products from this domain
    products = supabase.table("products") \
                       .select("id, domain") \
                       .eq("domain", domain) \
                       .execute().data

    if not products:
        return {
            "status": "error",
            "message": f"No products found in domain: {domain}"
        }

    trained = []
    skipped = []

    for p in products:
        uuid = p["id"]

        scraped = fetch_scraped_json(uuid)
        if not scraped:
            skipped.append(uuid)
            continue

        prediction = run_ml_on_scraped(scraped)

        upsert_model_output(
            uuid,
            model_name="pricing_model_v1",
            prediction_json=prediction
        )

        trained.append(uuid)

    return {
        "status": "complete",
        "domain": domain,
        "trained_count": len(trained),
        "trained_products": trained,
        "skipped_no_data": skipped
    }


# ------------------------------------------------------------------------------------
# 5️⃣ TRAIN ALL PRODUCTS (GLOBAL BUTTON)
# ------------------------------------------------------------------------------------
@app.post("/run-model-all")
def run_model_for_all():

    products = supabase.table("products").select("id").execute().data

    trained = []
    skipped = []

    for p in products:
        uuid = p["id"]

        scraped = fetch_scraped_json(uuid)
        if not scraped:
            skipped.append(uuid)
            continue

        prediction = run_ml_on_scraped(scraped)

        upsert_model_output(
            uuid,
            model_name="pricing_model_v1",
            prediction_json=prediction
        )

        trained.append(uuid)

    return {
        "status": "complete",
        "trained_count": len(trained),
        "trained_products": trained,
        "skipped_no_data": skipped
    }

