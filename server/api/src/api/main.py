from fastapi import FastAPI

app = FastAPI(title=__name__)


@app.get("/")
async def root():
    return {"message": "Hello World"}
