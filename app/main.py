from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.process import router as process_router

app = FastAPI(title="PPT AI Generator")

app.include_router(health_router)
app.include_router(process_router)

@app.get("/")
def root():
    return {"status": "running"}

