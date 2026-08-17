import pytest

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
    assert body["currency"] == "USD"


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
        "currency": "USD",
    }

    body = predict_from_payload(payload)

    assert body["currency"] == "USD"
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
        "currency": "USD",
    }

    one_item = predict_from_payload({**common, "Quantity": 1})
    seven_items = predict_from_payload({**common, "Quantity": 7})

    assert one_item["prediction"] != seven_items["prediction"]


def test_equivalent_currency_inputs_produce_equivalent_predictions():
    common = {
        "Branch": "A",
        "City": "Yangon",
        "Customer type": "Member",
        "Gender": "Female",
        "Product line": "Health and beauty",
        "Quantity": 7,
        "Payment": "Ewallet",
    }
    mmk_payload = {**common, "Unit price": 74.69 * 3500, "currency": "MMK"}
    usd_payload = {**common, "Unit price": 74.69, "currency": "USD"}

    mmk_result = predict_from_payload(mmk_payload)
    usd_result = predict_from_payload(usd_payload)

    assert usd_result["prediction"] == pytest.approx(mmk_result["prediction"])


def test_only_usd_display_currency_is_supported():
    payload = {
        "Branch": "A",
        "City": "Yangon",
        "Customer type": "Member",
        "Gender": "Female",
        "Product line": "Health and beauty",
        "Unit price": 74.69,
        "Quantity": 7,
        "Payment": "Ewallet",
        "currency": "USD",
    }

    body = predict_from_payload(payload)

    assert body["currency"] == "USD"
    assert body["model_unit"] == "DATASET_UNITS"
    assert body["prediction"] > 0


def test_predict_from_payload_rejects_unknown_currency():
    payload = {"currency": "EUR"}

    try:
        predict_from_payload(payload)
    except ValueError as exc:
        assert "Unsupported currency" in str(exc)
    else:
        raise AssertionError("Unknown currencies must be rejected")
