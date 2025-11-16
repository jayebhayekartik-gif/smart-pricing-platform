# dashboard/pages/3_Scraped_Data_Viewer.py
import streamlit as st
import pandas as pd
from dashboard.utils.product_selector import fetch_all_products
from dashboard.utils.scraped_data_access import fetch_scraped_data, fetch_scraped_json

st.set_page_config(page_title="Scraped Data Viewer", layout="wide")
st.title("📚 Scraped Data Viewer")

products = fetch_all_products()
if not products:
    st.sidebar.error("No products")
    st.stop()

product_map = {f"{p['name']} ({p.get('domain','')})": p["id"] for p in products}
selected = st.sidebar.selectbox("Choose product", list(product_map.keys()), key="sdv_product")
uuid = product_map[selected]

scraped_row = fetch_scraped_data(uuid)
if scraped_row:
    st.markdown("### Full scraped_data row")
    st.json(scraped_row)
    st.markdown("### data array (first 20 items)")
    st.json(scraped_row.get("data", [])[:20])
else:
    st.info("No scraped_data for this product")
