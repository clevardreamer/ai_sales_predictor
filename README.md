# Sales Prediction App

This project is deployed in two parts:

- Frontend: Streamlit UI in streamlit_app.py
- Backend (stable path): Flask API in app.py

## Local Run (Stable)

1. Install dependencies.

```bash
pip install -r requirements.txt
```

1. Start backend.

```bash
python app.py
```

1. Start frontend in a second terminal.

```bash
streamlit run streamlit_app.py --server.address 127.0.0.1 --server.port 8501
```

1. Open the app at <http://127.0.0.1:8501>.

## Environment Variable

- BACKEND_URL (default: <http://127.0.0.1:8000/predict>)

Set this in hosted frontend environments to your real backend URL.

## Hosting Notes

- Do not leave BACKEND_URL as localhost when deploying frontend and backend separately.
- Ensure model artifacts exist in models/ (best_model.joblib and related files).
- Use health checks at /health.
- UI includes a Check Backend Connection button.

## Optional FastAPI Backend

- FastAPI code exists in backend/main.py.
- Install pinned API dependencies to avoid version drift:

```bash
pip install -r backend/requirements.txt
```

## One-Click Start Scripts

- Windows: scripts/start_windows.bat
- Linux: scripts/start_linux.sh

Linux first-time setup:

```bash
chmod +x scripts/start_linux.sh
```

Run:

```bash
# Windows
scripts\start_windows.bat

# Linux
./scripts/start_linux.sh
```

## Deployment Checklist (Render / Railway)

- See docs/deployment_checklist_render_railway.md

## Render One-Click Blueprint

- Blueprint file: render.yaml

Use it in Render:

1. Push current branch to GitHub.
1. In Render, choose New +, then Blueprint.
1. Select this repository and apply.
1. After provisioning, set BACKEND_URL in sales-frontend to your backend predict URL.

## Smoke Test (Pre-Release Gate)

Run this before every release:

```bash
python scripts/smoke_test.py --base-url http://127.0.0.1:8000
```

For hosted backends:

```bash
python scripts/smoke_test.py --base-url https://<your-backend-domain>
```
