# dashboard/pages/2_Model_Comparison.py
import streamlit as st
import pandas as pd

from dashboard.utils.product_selector import fetch_all_products
from dashboard.utils.fetch_predictions import fetch_all_predictions, fetch_prediction_by_model

st.set_page_config(page_title="Model Comparison", layout="wide")
st.title("🧪 Model Comparison")

products = fetch_all_products()
if not products:
    st.sidebar.error("No products")
    st.stop()

product_map = {f"{p['name']} ({p.get('domain','')})": p["id"] for p in products}
selected_label = st.sidebar.selectbox("Choose product", list(product_map.keys()), key="mc_product")
selected_uuid = product_map[selected_label]

st.subheader("Model outputs history")
history = fetch_all_predictions(selected_uuid)
if not history:
    st.info("No model outputs")
    st.stop()

# Build DataFrame with model_name, predicted_at, predicted_price
rows = []
for r in history:
    p = r.get("prediction", {})
    rows.append({
        "model_name": r.get("model_name"),
        "predicted_at": r.get("predicted_at"),
        "predicted_price": p.get("predicted_price"),
        "confidence": p.get("confidence"),
        "version": p.get("model_version")
    })
df = pd.DataFrame(rows).sort_values("predicted_at", ascending=False)

st.dataframe(df.head(200))

# Quick compare latest values per model
st.markdown("### Latest value per model")
latest_by_model = df.groupby("model_name").first().reset_index()
st.dataframe(latest_by_model[["model_name","predicted_at","predicted_price","confidence","version"]])



