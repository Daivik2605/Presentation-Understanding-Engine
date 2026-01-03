from fastapi import FastAPI

app = FastAPI(title="PPT AI Generator")

@app.get("/")
def root():
    return {"status": "running"}
