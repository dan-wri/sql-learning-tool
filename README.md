# SQL Learning Tool

An interactive SQL learning app. Each learner has their own persistent SQLite training database. Passing challenge submissions are committed to it; failing ones are rolled back.

- `backend/`: FastAPI, Python 3.11+
- `frontend/`: React + Vite (JavaScript/JSX), CodeMirror 6

## Prerequisites

- Python 3.11 or newer
- Node.js 20.19 or newer (needed by Vite 7)

## Backend

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

When the backend starts, it builds `backend/data/template.db` if the file is missing or out of date. It creates each learner's database at `backend/data/learners/<uuid>.db` the first time that learner visits.

To rebuild the template by hand:

```sh
python -m app.db.build_template
```

To store data somewhere else, set `SQL_TOOL_DATA_DIR`.

Run the tests:

```sh
pytest
```

API docs are at http://localhost:8000/docs.

## Frontend

```sh
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Vite forwards `/api` requests to the backend on port 8000, so start the backend first.

Run the tests:

```sh
npm test
```

## How learner identity works

- On first visit, the browser creates a UUID and stores it in `localStorage` under `sqlLearningTool.learnerId`.
- Every API request sends it in the `X-Learner-Id` header.
- The backend only accepts UUIDs in standard (canonical) form, because the ID is used as part of a file path.
- To start over as a brand-new learner, clear that `localStorage` key.

## Changing the dataset

1. Edit `backend/app/db/schema.sql` or `backend/app/db/seed_data.py`.
2. Increase `SEED_VERSION` in `backend/app/db/build_template.py`.

Existing learner databases will then show a warning in the UI until the learner resets.
