from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import admin, auth, fridges, item_ops, items, recipes, recognize

app = FastAPI(title="The Leftover Bureau API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(fridges.router, prefix="/api")
app.include_router(items.router, prefix="/api")
app.include_router(item_ops.router, prefix="/api")
app.include_router(recipes.router, prefix="/api")
app.include_router(recognize.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
