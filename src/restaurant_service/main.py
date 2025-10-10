from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
import redis
import os

app = FastAPI(name="restaurant_service")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://user:password@postgres:5432/restaurant_db")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

@app.get("/health")
async def root():
    return {"service": "restaurant_service", "status": "healthy"}


@app.get("/check_redis")
async def check_redis():
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    try:
        r.ping()
        return {"redis": "connected"}
    except redis.ConnectionError:
        return JSONResponse(status_code=500, content={"redis": "not connected"})

@app.get("/check_db")
async def check_db():
    engine = create_engine(DATABASE_URL)
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"database": "connected"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"database": "not connected", "error": str(e)})
