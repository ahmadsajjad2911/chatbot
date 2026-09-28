from fastapi import FastAPI

app = FastAPI(title="OpenChat Backend", version="0.1.0")


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Welcome to OpenChat API"}


@app.get("/health")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
