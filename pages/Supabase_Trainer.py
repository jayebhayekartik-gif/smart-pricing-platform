# dashboard/pages/Supabase_Trainer.py

import streamlit as st
import pandas as pd

from dashboard.utils.product_selector import get_product_by_uuid
from dashboard.utils.scraped_data_access import fetch_scraped_json   # ← FIXED
from dashboard.utils.ml_json_pipeline import run_pipeline_json       # if name differs, tell me
from dashboard.utils.insert_model_output import upsert_model_output


# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
st.title("🟪 Supabase Trainer (Auto)")

# Get selected product UUID from app.py sidebar
product_uuid = st.session_state.get("selected_product_uuid", None)

if not product_uuid:
    st.error("No product selected! Go to the sidebar and choose a product.")
    st.stop()


# Show selected product metadata
product_info = get_product_by_uuid(product_uuid)
if product_info:
    st.subheader(f"Product: {product_info['name']} ({product_info.get('domain','')})")
    st.write(f"Your Price: {product_info['your_price']}")
else:
    st.warning("Product metadata not found.")


# ---------------------------------------------------------
# Trainer button
# ---------------------------------------------------------
if st.button("Run Trainer (fetch → train → upload)"):

    # -------------------------
    # FETCH SCRAPED JSON
    # -------------------------
    with st.spinner("Fetching scraped JSON from Supabase..."):
        scraped_json = fetch_scraped_json(product_uuid)

    if not scraped_json:
        st.error("No scraped data found for this product!")
        st.stop()

    st.success(f"Fetched {len(scraped_json)} scraped records.")


    # -------------------------
    # RUN ML MODEL
    # -------------------------
    with st.spinner("Training ML model on scraped JSON..."):
        model_output = run_pipeline_json(scraped_json)

    st.success("Training complete.")


    # -------------------------
    # UPSERT MODEL OUTPUT
    # -------------------------
    with st.spinner("Uploading prediction to Supabase..."):

        saved = upsert_model_output(
            product_uuid=product_uuid,
            model_name="pricing_model_v1",     # you can change model name
            prediction_json=model_output,      # JSON payload
            metadata_json={"samples_used": len(scraped_json)}
        )

    st.success("Model prediction uploaded successfully!")

    st.subheader("📦 Uploaded Prediction JSON")
    st.json(saved[0] if saved else model_output)




