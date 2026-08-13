import streamlit as st

from app import predict_from_payload


@st.cache_resource
def load_predictor():
    return predict_from_payload

st.set_page_config(page_title="Sales Prediction App", layout="wide")
st.title("Sales Prediction App")
st.write("Enter customer and product details to estimate the sales outcome.")
st.caption("Predictions run locally in this Streamlit app.")

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
        result = load_predictor()(payload)
        prediction = result.get("prediction")
        if prediction is None:
            st.error("Prediction response does not contain 'prediction'.")
            st.json(result)
        else:
            st.success(f"Predicted Sales: {prediction}")
    except Exception as exc:
        st.error(f"Prediction failed: {exc}")
