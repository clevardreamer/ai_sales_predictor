# Sales Prediction App

This is a self-contained Streamlit app that predicts retail sales with a trained scikit-learn model. Predictions run locally inside the Streamlit process; no separate backend service or environment variables are required.

## Currency Handling

The model is trained on the dataset's original monetary scale, which is treated as USD for this prototype because the source CSV does not declare a currency and its values are already on a dollar-like scale. Currency is not a model feature. The app converts the entered unit price to USD before inference and converts the predicted gross income back to the selected currency afterward. Omitting currency from API requests preserves the model-scale behavior.

The prototype uses fixed configurable rates: `1 USD = 3500 MMK`, `1 USD = 1600 NGN`, `1 USD = 0.79 GBP`, and `1 USD = 0.92 EUR`. Set `MMK_PER_USD`, `NGN_PER_USD`, `GBP_PER_USD`, or `EUR_PER_USD` before starting the app when rates need to be updated. These rates are not live market data.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open the URL printed by Streamlit, normally <http://localhost:8501>.

## Deploy To Streamlit Community Cloud

1. Create an app at <https://share.streamlit.io>.
1. Select the `main` branch of this repository.
1. Set the entrypoint to `streamlit_app.py`.
1. Deploy.

The deployment requires the tracked files `models/best_model.joblib` and `data/processed/processed.csv`. Do not remove or rename either file.

## Development Assets

Raw datasets, notebooks, training modules, and test scripts are retained for future model development. Generated metrics, prediction outputs, and auxiliary model artifacts are excluded from Git.
