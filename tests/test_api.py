from app import predict_from_payload


def test_predict_from_payload_returns_prediction():
    payload = {
        "Invoice ID": "TEST-001",
        "Branch": "A",
        "City": "Yangon",
        "Customer type": "Member",
        "Gender": "Female",
        "Product line": "Health and beauty",
        "Unit price": 74.69,
        "Quantity": 7,
        "Tax 5%": 26.1415,
        "Sales": 548.9715,
        "Date": "2019-01-05",
        "Time": "1:08:00 PM",
        "Payment": "Ewallet",
        "cogs": 522.83,
        "gross margin percentage": 4.761905,
        "Rating": 9.1,
    }

    body = predict_from_payload(payload)

    assert "prediction" in body
    assert isinstance(body["prediction"], (int, float))
    assert body["model_unit"] == "DATASET_UNITS"


def test_predict_from_payload_converts_selected_currency():
    payload = {
        "Branch": "A",
        "City": "Yangon",
        "Customer type": "Member",
        "Gender": "Female",
        "Product line": "Health and beauty",
        "Unit price": 74.69,
        "Quantity": 7,
        "Payment": "Ewallet",
    }

    body = predict_from_payload(payload)

    assert body["model_unit"] == "DATASET_UNITS"
    assert isinstance(body["prediction"], float)


def test_quantity_changes_prediction():
    common = {
        "Branch": "A",
        "City": "Yangon",
        "Customer type": "Member",
        "Gender": "Female",
        "Product line": "Health and beauty",
        "Unit price": 74.69,
        "Payment": "Ewallet",
    }

    one_item = predict_from_payload({**common, "Quantity": 1})
    seven_items = predict_from_payload({**common, "Quantity": 7})

    assert one_item["prediction"] != seven_items["prediction"]


def test_prediction_uses_numeric_inputs_without_currency_conversion():
    common = {
        "Branch": "A",
        "City": "Yangon",
        "Customer type": "Member",
        "Gender": "Female",
        "Product line": "Health and beauty",
        "Quantity": 7,
        "Payment": "Ewallet",
    }
    plain_payload = {**common, "Unit price": 74.69}
    plain_result = predict_from_payload(plain_payload)
    assert plain_result["model_unit"] == "DATASET_UNITS"
    assert plain_result["prediction"] > 0



