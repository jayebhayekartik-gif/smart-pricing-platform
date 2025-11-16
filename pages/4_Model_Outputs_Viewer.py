# dashboard/pages/4_Model_Outputs_Viewer.py
import streamlit as st
import pandas as pd
from dashboard.utils.product_selector import fetch_all_products
from dashboard.utils.fetch_predictions import fetch_all_predictions

st.set_page_config(page_title="Model Outputs Viewer", layout="wide")
st.title("📦 Model Outputs Viewer")

products = fetch_all_products()
if not products:
    st.sidebar.error("No products")
    st.stop()

product_map = {f"{p['name']} ({p.get('domain','')})": p["id"] for p in products}
selected = st.sidebar.selectbox("Choose product", list(product_map.keys()), key="mov_product")
uuid = product_map[selected]

history = fetch_all_predictions(uuid)
if not history:
    st.info("No model outputs yet")
    st.stop()

rows = []
for r in history[::-1]:
    p = r.get("prediction", {})
    rows.append({
        "predicted_at": r.get("predicted_at"),
        "model_name": r.get("model_name"),
        "predicted_price": p.get("predicted_price"),
        "confidence": p.get("confidence"),
        "version": p.get("model_version"),
        "metadata": r.get("metadata")
    })

st.dataframe(pd.DataFrame(rows).head(200))
