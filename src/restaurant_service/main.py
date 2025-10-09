from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, text
import redis

app = FastAPI(name="restaurant_service")

@app.get("/health")
async def root():
    return {"service": "restaurant_service", "status": "healthy"}


@app.get("/check_redis")
async def check_redis():
    r = redis.Redis(host='redis', port=6379, db=0)
    try:
        r.ping()
        return {"redis": "connected"}
    except redis.ConnectionError:
        return JSONResponse(status_code=500, content={"redis": "not connected"})

# @app.get("/check_db")
# async def check_db():
#     engine = create_engine('postgresql+psycopg2://user:password@db:5432/restaurant_db')
#     try:
#         with engine.connect() as connection:
#             result = connection.execute(text("SELECT 1"))
#             if result.fetchone()[0] == 1:
#                 return {"database": "connected"}
#             else:
#                 return JSONResponse(status_code=500, content={"database": "not connected"})
#     except Exception as e:
#         return JSONResponse(status_code=500, content={"database": "not connected", "error": str(e)})
