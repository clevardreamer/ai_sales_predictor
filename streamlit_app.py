import streamlit as st

from app import predict_from_payload


@st.cache_resource
def load_predictor():
    return predict_from_payload

st.set_page_config(page_title="Sales Prediction App", layout="wide")
st.title("Sales Prediction App")
st.write("Enter customer and product details to estimate the sales outcome.")
st.caption("Predictions use the dataset's original numeric units. No currency conversion is applied.")

branch = st.selectbox("Branch", ["A", "B", "C"], index=None, placeholder="Select a branch")
city = st.selectbox("City", ["Yangon", "Mandalay", "Naypyitaw"], index=None, placeholder="Select a city")
customer_type = st.selectbox("Customer Type", ["Member", "Normal"], index=None, placeholder="Select customer type")
gender = st.selectbox("Gender", ["Male", "Female"], index=None, placeholder="Select gender")
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
    index=None,
    placeholder="Select a product line",
)
unit_price = st.number_input("Unit Price", min_value=0.0, value=None, step=0.01, placeholder="Enter unit price")
quantity = st.number_input("Quantity", min_value=1, value=None, step=1, placeholder="Enter quantity")
payment = st.selectbox("Payment Method", ["Cash", "Credit card", "Ewallet"], index=None, placeholder="Select payment method")
if st.button("Predict Sales"):
    fields = {
        "Branch": branch,
        "City": city,
        "Customer type": customer_type,
        "Gender": gender,
        "Product line": product_line,
        "Unit price": unit_price,
        "Quantity": quantity,
        "Payment": payment,
    }
    missing_fields = [name for name, value in fields.items() if value is None]

    if missing_fields:
        st.warning("Please complete all fields before predicting.")
    else:
        try:
            result = load_predictor()(fields)
            prediction = result.get("prediction")
            if prediction is None:
                st.error("Prediction response does not contain 'prediction'.")
                st.json(result)
            else:
                st.success(f"Predicted Gross Income: USD {prediction:,.2f}")
        except Exception as exc:
            st.error(f"Prediction failed: {exc}")
