# Loan Risk Assessment Prediction System

This repository now contains a production-friendly loan risk pipeline built around a frozen LightGBM model artifact at `models/LightGBM.pkl`.

The model is trained from the Home Credit dataset using the same business fields that appear in the project schema:

- `gender`
- `owns_car`
- `owns_realty`
- `income_total`
- `education_type`
- `family_status`
- `housing_type`
- `occupation_type`
- `cnt_children`
- `family_members`
- `credit_amount`
- `annuity_amount`
- `goods_price`
- `loan_type`

## Architecture

- Animated PySide6 desktop dashboard in `desktop_app.py`
- FastAPI backend in `backend/app/main.py`
- Frozen model artifact in `models/LightGBM.pkl`
- Prediction payloads shaped around `customers` and `loan_applications`

## Train the model

```bash
python training/train.py
```

This reads `dataset/train.csv`, trains the pipeline, and saves:

- `models/LightGBM.pkl`
- `models/LightGBM.metadata.json`

## Run the API

```bash
uvicorn backend.app.main:app --reload
```

API routes:

- `GET /health`
- `GET /db-health`
- `GET /customers`
- `GET /customer/{customer_id}`
- `GET /predictions`
- `POST /predict/{customer_id}`

## Run the dashboard

```bash
python desktop_app.py
```

Demo login:

- Username: `bankadmin`
- Password: `admin123`

If you still want the web version, you can run:

```bash
streamlit run frontend/dashboard.py
```

## Docker deployment

Run the full stack locally with PostgreSQL, FastAPI, and Streamlit:

```bash
docker compose up --build
```

Services:

- Frontend: `http://localhost:8501`
- Backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

## CI/CD

GitHub Actions is configured through the workflow file in `.github/workflows/ci.yml`.

- Push to `main` or open a pull request to run smoke tests and Docker image builds.
- If you want to publish images or deploy automatically, we can add a second workflow with registry credentials and host secrets.

## Core tables

The project SQL schema is documented in `docs/schema.sql`.
