# Run NEXUS Without Docker

This is the recommended path when Docker cannot download its image dependencies.
The API uses its in-memory semantic cache locally, so PostgreSQL and Redis are
not required for the dashboard demo.

Open two PowerShell terminals in the repository root.

## Terminal 1: API

```powershell
cd backend
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload
```

Wait for `Uvicorn running on http://127.0.0.1:8000`.

## Terminal 2: dashboard

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` and the live WebSocket to the
API automatically.

## Verify

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
python -m pytest
```
