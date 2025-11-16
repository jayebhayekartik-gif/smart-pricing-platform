from fastapi import FastAPI
from pydantic import BaseModel

from .scraped_data import fetch_scraped_json
from .ml_pipeline import run_ml_on_scraped
from .model_output import upsert_model_output

app = FastAPI(title="Smart Pricing ML API")

class PredictRequest(BaseModel):
    product_uuid: str
    model_name: str = "pricing_model_v1"

@app.post("/run-model")
def run_model(req: PredictRequest):
    
    # Step 1 — get scraped data
    scraped = fetch_scraped_json(req.product_uuid)
    if not scraped:
        return {"status": "error", "message": "No scraped data found"}

    # Step 2 — run ML pipeline
    final_prediction_json = run_ml_on_scraped(scraped)
    if not final_prediction_json:
        return {"status": "error", "message": "ML pipeline returned nothing"}

    # Step 3 — save into Supabase model_outputs
    saved = upsert_model_output(
        req.product_uuid,
        req.model_name,
        final_prediction_json
    )

    return {
        "status": "success",
        "product_uuid": req.product_uuid,
        "model_name": req.model_name,
        "saved": saved,
        "prediction": final_prediction_json
    }
