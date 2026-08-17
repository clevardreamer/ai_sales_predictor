# Sales Prediction App

This is a self-contained Streamlit app that predicts retail sales with a trained scikit-learn model. Predictions run locally inside the Streamlit process; no separate backend service or environment variables are required.

## Currency Handling

The model is trained on the dataset's original numeric scale. The source CSV does not declare a currency, so predictions are reported as `DATASET_UNITS`; the selected currency is currently a display label only. Currency is not a model feature, and no unsupported exchange-rate conversion is applied.

To provide real USD, EUR, GBP, MMK, or NGN amounts, the dataset currency must first be verified and the model retrained or an explicitly documented base-currency conversion must be configured.

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
