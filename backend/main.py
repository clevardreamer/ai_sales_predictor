import os
import time
import logging
from functools import wraps
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, root_validator, validator
import joblib
import pandas as pd


MODEL_PATH = os.getenv("MODEL_PATH", "models/best_model.joblib")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "")
RATE_LIMIT_PER_MIN = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("sales_api")

app = FastAPI(title="Sales Prediction API", version="1.0.0")

origins = [o.strip() for o in ALLOWED_ORIGINS.split(",") if o.strip()]
if not origins:
    origins = ["http://localhost:8501", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

_requests = defaultdict(list)


def rate_limiter(limit_per_min: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            ip = request.client.host if request.client else "unknown"
            now = time.time()
            window_start = now - 60
            timestamps = [t for t in _requests[ip] if t > window_start]
            timestamps.append(now)
            _requests[ip] = timestamps
            if len(timestamps) > limit_per_min:
                logger.warning("Rate limit exceeded for IP %s", ip)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests, please slow down.",
                )
            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


class PredictionInput(BaseModel):
    Branch: str = Field(..., description="Branch code or name")
    City: str
    Customer_type: str = Field(..., alias="Customer type")
    Gender: str
    Product_line: str = Field(..., alias="Product line")
    Unit_price: float = Field(..., ge=0.0, alias="Unit price")
    Quantity: int = Field(..., ge=1)
    Payment: str
    Date: str | None = Field(None, description="ISO date YYYY-MM-DD")
    Time: str | None = Field(None, description="HH:MM")

    class Config:
        allow_population_by_field_name = True

    @root_validator(pre=True)
    def harmonize_underscore_keys(cls, values):
        if not isinstance(values, dict):
            return values
        if "Customer_type" in values and "Customer type" not in values:
            values["Customer type"] = values["Customer_type"]
        if "Product_line" in values and "Product line" not in values:
            values["Product line"] = values["Product_line"]
        if "Unit_price" in values and "Unit price" not in values:
            values["Unit price"] = values["Unit_price"]
        return values

    @validator("Branch", "City", "Customer_type", "Gender", "Product_line", "Payment")
    def not_empty(cls, value):
        if isinstance(value, str) and not value.strip():
            raise ValueError("must not be empty")
        return value


try:
    model = joblib.load(MODEL_PATH)
    logger.info("Model loaded from %s", MODEL_PATH)
except Exception as exc:
    logger.exception("Failed to load model: %s", exc)
    model = None


@app.get("/")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.get("/health")
def health_alias():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")
@rate_limiter(RATE_LIMIT_PER_MIN)
async def predict(request: Request, payload: PredictionInput):
    if model is None:
        logger.error("Prediction requested but model is not loaded")
        raise HTTPException(status_code=500, detail="Model not available")

    try:
        data = pd.DataFrame([
            {
                "Branch": payload.Branch,
                "City": payload.City,
                "Customer type": payload.Customer_type,
                "Gender": payload.Gender,
                "Product line": payload.Product_line,
                "Unit price": payload.Unit_price,
                "Quantity": payload.Quantity,
                "Payment": payload.Payment,
                "Date": payload.Date,
                "Time": payload.Time,
            }
        ])

        if "Sales" in data.columns or "gross income" in data.columns:
            logger.error("Input contains forbidden target columns")
            raise HTTPException(status_code=400, detail="Input contains forbidden field")

        preds = model.predict(data)
        prediction = float(preds[0])

        logger.info("Prediction served for IP %s: %.4f", request.client.host if request.client else "unknown", prediction)
        return {"prediction": prediction}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Prediction error: %s", exc)
        raise HTTPException(status_code=500, detail="Prediction failed")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
