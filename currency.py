import os


BASE_CURRENCY = "USD"
USD_PER_UNIT = {
    "USD": 1.0,
    "MMK": 1.0 / float(os.getenv("MMK_PER_USD", "3500")),
    "NGN": 1.0 / float(os.getenv("NGN_PER_USD", "1600")),
    "GBP": float(os.getenv("GBP_PER_USD", "0.79")),
    "EUR": float(os.getenv("EUR_PER_USD", "0.92")),
}


def normalize_currency(currency: str | None) -> str:
    code = (currency or BASE_CURRENCY).strip().upper()
    if code not in USD_PER_UNIT:
        supported = ", ".join(sorted(USD_PER_UNIT))
        raise ValueError(f"Unsupported currency '{currency}'. Use one of: {supported}")
    return code


def to_base_currency(amount: float, currency: str | None) -> float:
    code = normalize_currency(currency)
    return float(amount) * USD_PER_UNIT[code]


def from_base_currency(amount: float, currency: str | None) -> float:
    code = normalize_currency(currency)
    return float(amount) / USD_PER_UNIT[code]