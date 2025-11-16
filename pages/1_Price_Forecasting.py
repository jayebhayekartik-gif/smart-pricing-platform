# dashboard/pages/1_Price_Forecasting.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from dashboard.utils.product_selector import fetch_all_products, get_product_by_uuid
from dashboard.utils.scraped_data_access import fetch_scraped_json
from dashboard.utils.fetch_predictions import fetch_latest_prediction, fetch_all_predictions

st.set_page_config(page_title="Price Forecasting", layout="wide")
st.title("📊 Price Forecasting (Semi-Advanced)")

# Sidebar product selector
products = fetch_all_products()
if not products:
    st.sidebar.error("No products found")
    st.stop()

product_map = {f"{p['name']} ({p.get('domain','')})": p["id"] for p in products}
selected_label = st.sidebar.selectbox("Choose product", list(product_map.keys()), key="pf_product")
selected_uuid = product_map[selected_label]
st.session_state["selected_product_uuid"] = selected_uuid

# product info
prod = get_product_by_uuid(selected_uuid)
st.subheader(f"{prod.get('name')} — {prod.get('domain','')}")
st.write("Your price:", prod.get("your_price"))

# fetch latest scraped JSON array for feature inspection
scraped_array = fetch_scraped_json(selected_uuid) or []
st.markdown("### Latest scraped items (sample 5)")
st.json(scraped_array[:5])

# latest prediction
latest = fetch_latest_prediction(selected_uuid)
if not latest:
    st.warning("No model output yet. Run Trainer.")
    st.stop()

pred = latest.get("prediction", {})
pred_price = pred.get("predicted_price")
if pred_price is None:
    st.error("Latest prediction JSON does not contain 'predicted_price'")
    st.stop()

# compute simple KPI: last observed price from scraped_array (best-effort)
def find_price_from_scraped(arr):
    # try common keys: price, your_price, listing_price, seller_price
    for item in reversed(arr):
        for key in ["price", "your_price", "listing_price", "seller_price", "mrp"]:
            if item.get(key) is not None:
                try:
                    s = str(item.get(key)).replace(",", "")
                    return float(''.join([c for c in s if c.isdigit() or c=='.' or c=='-']))
                except:
                    continue
    return None

today_price = find_price_from_scraped(scraped_array) or prod.get("your_price") or 0.0
tomorrow_pred = float(pred_price)
pct_change = (tomorrow_pred - today_price) / max(abs(today_price), 1e-6) * 100

# KPIs
c1, c2, c3 = st.columns(3)
c1.metric("Observed Price (latest)", f"₹{today_price:,.2f}")
c2.metric("Predicted Price (tomorrow)", f"₹{tomorrow_pred:,.2f}", f"{pct_change:+.2f}%")
c3.metric("Confidence", f"{pred.get('confidence', 'N/A')}")

# 7-day sparkline from prediction history
hist = fetch_all_predictions(selected_uuid)
pred_series = []
if hist:
    for r in hist:
        p = r.get("prediction", {})
        if p and p.get("predicted_price") is not None:
            pred_series.append(float(p["predicted_price"]))
if pred_series:
    st.markdown("### 7-day Ensemble Forecast")
    dfp = pd.DataFrame({"t": list(range(1, len(pred_series)+1)), "pred": pred_series})
    fig = px.line(dfp.tail(7), x="t", y="pred", markers=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Not enough prediction history for sparkline")

# show table of recent predictions
st.markdown("### Recent predictions")
if hist:
    rows = []
    for r in hist[::-1]:
        p = r.get("prediction", {})
        rows.append({
            "predicted_at": r.get("predicted_at"),
            "model": r.get("model_name"),
            "predicted_price": p.get("predicted_price"),
            "confidence": p.get("confidence"),
            "version": p.get("model_version")
        })
    st.dataframe(pd.DataFrame(rows).head(50))
else:
    st.info("No predictions to show")


