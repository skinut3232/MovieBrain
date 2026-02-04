from fastapi import FastAPI

from app.routers import auth, catalog, profiles

app = FastAPI(title="MovieBrain", version="0.1.0")

app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(catalog.router)


@app.get("/health")
def health():
    return {"status": "ok"}
