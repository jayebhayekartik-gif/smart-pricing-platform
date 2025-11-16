# dashboard/pages/0_Home.py
import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard.utils.product_selector import fetch_all_products, get_product_by_uuid
from dashboard.utils.scraped_data_access import fetch_scraped_data, fetch_scraped_json
from dashboard.utils.fetch_predictions import fetch_latest_prediction, fetch_all_predictions

st.set_page_config(page_title="Smart Pricing — Overview", layout="wide")
st.title("🏷️ Smart Pricing — Overview (Semi-Advanced)")

# Sidebar product selector
products = fetch_all_products()
if not products:
    st.sidebar.error("No products in Supabase.")
    st.stop()

product_map = {f"{p['name']} ({p.get('domain','')})": p["id"] for p in products}
selected_label = st.sidebar.selectbox("Choose product", list(product_map.keys()), key="overview_product")
selected_uuid = product_map[selected_label]
st.session_state["selected_product_uuid"] = selected_uuid

# Header
prod = get_product_by_uuid(selected_uuid)
st.subheader(f"{prod.get('name')} — {prod.get('domain','')}")
st.write("Your price:", prod.get("your_price"))

# Latest scraped
st.markdown("#### 📦 Latest scraped data")
scraped_row = fetch_scraped_data(selected_uuid)
if scraped_row:
    st.caption(f"Scraped at: {scraped_row.get('scraped_at')}")
    st.json(scraped_row.get("data", []))
else:
    st.info("No scraped data")

# Latest prediction
st.markdown("#### 🤖 Latest prediction")
latest = fetch_latest_prediction(selected_uuid)
if latest:
    pred = latest.get("prediction", {})
    st.json(pred)
    if pred.get("predicted_price") is not None:
        st.metric("Predicted Price", f"₹{pred['predicted_price']:.2f}", delta=None)
else:
    st.info("No model outputs")

# Prediction history sparkline (last 7)
st.markdown("#### 📈 Prediction history (7 latest)")
history = fetch_all_predictions(selected_uuid)
if history:
    # extract predicted_price and predicted_at
    records = []
    for r in history:
        p = r.get("prediction", {})
        if p and p.get("predicted_price") is not None:
            records.append({"predicted_at": r.get("predicted_at"), "predicted_price": float(p["predicted_price"])})
    if records:
        dfh = pd.DataFrame(records).sort_values("predicted_at")
        fig = px.line(dfh.tail(7), x="predicted_at", y="predicted_price", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No numeric predicted_price entries found")
else:
    st.info("No prediction history")









