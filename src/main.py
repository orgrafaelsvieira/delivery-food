from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/v2")
async def root():
    return {"message": "Hello World! v2"}

@app.post("/items/")
async def create_item(name: str):
    return {"name": name, "message": "Item created"}
