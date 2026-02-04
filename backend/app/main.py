from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, catalog, flags, lists, profiles, recommend, watches

app = FastAPI(title="MovieBrain", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(catalog.router)
app.include_router(watches.router)
app.include_router(lists.router)
app.include_router(flags.router)
app.include_router(recommend.router)


@app.get("/health")
def health():
    return {"status": "ok"}
