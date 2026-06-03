# CardioSense Full-stack Dashboard

This repo now includes a production-style React + FastAPI version alongside the original Streamlit app.

## Structure

```text
frontend/
  src/components/
  src/pages/
  src/services/
  src/hooks/
  src/layouts/

backend/
  main.py
  routes/
  models/
  prediction/
  database/
  utils/
```

## Backend

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
Copy-Item backend\.env.example .env
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API uses the existing trained model and config:

- `src/config/config.yaml`
- `models/trained_models/best_model.pkl`
- `models/trained_models/scaler.pkl`
- `models/trained_models/encoder.pkl`

## Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Open `http://localhost:5173`.

If Supabase keys are empty, the frontend and backend run in local demo mode. Add these values to enable real auth and stored history:

```text
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
```

## Supabase

1. Create a Supabase project.
2. Run `SUPABASE_SCHEMA.sql` in the SQL editor.
3. Enable email auth in Authentication settings.
4. Add user metadata during signup: `role` can be `doctor`, `admin`, or `patient`.

## Deployment

Frontend on Vercel:

- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Env vars: `VITE_API_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`

Backend on Render or Railway:

- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Install command: `pip install -r backend/requirements.txt`
- Env vars: Supabase keys and `CORS_ORIGINS_RAW=https://your-vercel-app.vercel.app`

## Medical Note

CardioSense is a clinical decision-support prototype. It should not be used as a standalone diagnosis tool without clinician review and validation on the target population.
