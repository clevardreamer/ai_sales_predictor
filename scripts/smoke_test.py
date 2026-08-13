import argparse
import json
import sys
from typing import Any

import requests


def assert_ok(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_smoke_test(base_url: str, timeout: float) -> None:
    health_url = f"{base_url}/health"
    predict_url = f"{base_url}/predict"

    health_resp = requests.get(health_url, timeout=timeout)
    assert_ok(health_resp.status_code == 200, f"Health check failed: {health_resp.status_code}")

    payload: dict[str, Any] = {
        "Branch": "A",
        "City": "Yangon",
        "Customer type": "Member",
        "Gender": "Male",
        "Product line": "Health and beauty",
        "Unit price": 50.0,
        "Quantity": 5,
        "Payment": "Cash",
    }

    predict_resp = requests.post(predict_url, json=payload, timeout=timeout)
    assert_ok(
        predict_resp.status_code == 200,
        f"Predict endpoint failed: {predict_resp.status_code} {predict_resp.text}",
    )

    body = predict_resp.json()
    assert_ok("prediction" in body, f"Missing 'prediction' in response: {json.dumps(body)}")
    prediction = body["prediction"]
    assert_ok(
        isinstance(prediction, (int, float)),
        f"Prediction must be numeric, got {type(prediction).__name__}",
    )

    print("SMOKE TEST PASSED")
    print(f"health={health_url}")
    print(f"predict={predict_url}")
    print(f"prediction={prediction}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test for health and predict endpoints")
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Backend base URL (default: http://127.0.0.1:8000)",
    )
    parser.add_argument("--timeout", type=float, default=10.0, help="Request timeout in seconds")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    try:
        run_smoke_test(base_url=base_url, timeout=args.timeout)
    except Exception as exc:
        print(f"SMOKE TEST FAILED: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
