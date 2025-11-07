from fastapi import FastAPI

from trailine_model.example import example


app = FastAPI(title=__name__)

@app.get("/")
async def root():
    example()
    return {"message": "Hello World"}
