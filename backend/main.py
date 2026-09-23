"""FastAPI entry point for the OpportunityOS collection layer."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.research import router as research_router

app = FastAPI(title="OpportunityOS Backend", version="0.1.0")

# Development-friendly CORS. Restrict these origins before production deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(research_router)
