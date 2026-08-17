MODEL_UNIT = "DATASET_UNITS"
DISPLAY_CURRENCY = "USD"
SUPPORTED_CURRENCIES = (DISPLAY_CURRENCY,)


def normalize_currency(currency: str | None) -> str:
    code = (currency or BASE_CURRENCY).strip().upper()
    if code not in SUPPORTED_CURRENCIES:
        supported = ", ".join(SUPPORTED_CURRENCIES)
        raise ValueError(f"Unsupported currency '{currency}'. Use one of: {supported}")
    return code


def to_base_currency(amount: float, currency: str | None) -> float:
    normalize_currency(currency)
    return float(amount)


def from_base_currency(amount: float, currency: str | None) -> float:
    normalize_currency(currency)
    return float(amount)