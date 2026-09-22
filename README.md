# OpportunityOS backend

This repository currently contains the FastAPI and SerpApi raw-data collection layer.

## Run locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn main:app --reload
```

Set `SERPAPI_API_KEY` in the root `.env` file before calling `/research`.

## Try it

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/research \
  -H 'Content-Type: application/json' \
  -d '{"topic":"Drone Components","location":"India"}'
```

If the API key is missing, `/research` returns each source with an explanatory `error` field and no fabricated results.
