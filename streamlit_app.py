import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/predict")
HEALTH_URL = BACKEND_URL.replace("/predict", "/health") if BACKEND_URL.endswith("/predict") else BACKEND_URL


def check_backend_health() -> tuple[bool, str]:
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        response.raise_for_status()
        return True, f"Backend is reachable at {HEALTH_URL}"
    except requests.RequestException as exc:
        return False, f"Backend health check failed: {exc}"

st.set_page_config(page_title="Sales Prediction App", layout="wide")
st.title("Sales Prediction App")
st.write("Enter customer and product details to estimate the sales outcome.")
st.caption(f"Prediction endpoint: {BACKEND_URL}")

if st.button("Check Backend Connection"):
    ok, message = check_backend_health()
    if ok:
        st.success(message)
    else:
        st.error(message)

branch = st.selectbox("Branch", ["A", "B", "C"], index=0)
city = st.selectbox("City", ["Yangon", "Mandalay", "Naypyitaw"], index=0)
customer_type = st.selectbox("Customer Type", ["Member", "Normal"], index=0)
gender = st.selectbox("Gender", ["Male", "Female"], index=0)
product_line = st.selectbox(
    "Product Line",
    [
        "Health and beauty",
        "Electronic accessories",
        "Home and lifestyle",
        "Sports and travel",
        "Food and beverages",
        "Fashion accessories",
    ],
    index=0,
)
unit_price = st.number_input("Unit Price", min_value=0.0, value=50.0, step=0.01)
quantity = st.number_input("Quantity", min_value=1, value=5, step=1)
payment = st.selectbox("Payment Method", ["Cash", "Credit card", "Ewallet"], index=0)

if st.button("Predict Sales"):
    payload = {
        "Branch": branch,
        "City": city,
        "Customer type": customer_type,
        "Gender": gender,
        "Product line": product_line,
        "Unit price": unit_price,
        "Quantity": quantity,
        "Payment": payment,
    }

    try:
        response = requests.post(BACKEND_URL, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        prediction = result.get("prediction")
        if prediction is None:
            st.error("Prediction response does not contain 'prediction'.")
            st.json(result)
        else:
            st.success(f"Predicted Sales: {prediction}")
    except requests.RequestException as exc:
        st.error(f"Prediction request failed: {exc}")
