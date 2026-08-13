# Deployment Checklist (Render / Railway)

## 1. Repository and Runtime

- Confirm the default branch is healthy and contains the latest tested changes.
- Confirm Python runtime version in platform settings matches local runtime target.
- Install dependencies from requirements.txt and generate the model during the backend build.

## 2. Service Layout

- Frontend service: streamlit_app.py
- Backend service: app.py
- Prefer separate services for frontend and backend in production.
- Render Blueprint file: render.yaml

Render Blueprint quick start:

1. Push render.yaml to your default branch.
1. In Render, click New +, then Blueprint.
1. Select this repository and apply the Blueprint.
1. After both services are created, open sales-frontend settings.
1. Set BACKEND_URL to your backend predict URL.

Example:

`https://sales-backend.onrender.com/predict`

## 3. Environment Variables

Set these before first deploy:

- BACKEND_URL=`https://your-backend-domain/predict`
- Optional: PORT (if platform requires explicit binding)

Important:

- Never leave BACKEND_URL pointing to localhost in cloud deployment.

## 4. Start Commands

Backend build command:

```bash
pip install -r requirements.txt && python -m src.train --input-path data/processed/processed.csv
```

Backend start command (Flask):

```bash
python app.py
```

The model is generated during the Render build. Do not rely on training during API startup.

Frontend (Streamlit):

```bash
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port $PORT
```

## 5. Artifacts and Data

- Verify models/best_model.joblib is present in deployed build.
- Verify data/processed/processed.csv is present if needed by runtime logic.
- Confirm file paths are relative and valid in container filesystem.

## 6. Health and Smoke Validation

After deploy:

- Check backend health endpoint: /health
- Run smoke test against deployed backend:

```bash
python scripts/smoke_test.py --base-url https://your-backend-domain
```

- Open frontend and run one real prediction through the UI.

## 7. CORS and Networking

- If using FastAPI backend path later, ensure ALLOWED_ORIGINS includes frontend domain.
- Confirm frontend can reach backend over HTTPS.

## 8. Observability

- Review startup logs for import or dependency issues.
- Review request logs for /predict failures.
- Set alerting for repeated 5xx responses.

## 9. Release Gate (Required)

Before every release, run:

```bash
python scripts/smoke_test.py --base-url http://127.0.0.1:8000
```

Only release when smoke test passes.

## 10. Rollback Plan

- Keep last known good image or deploy snapshot.
- If release fails health/smoke checks, roll back immediately.
- Re-run smoke test after rollback confirmation.
