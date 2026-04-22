from fastapi import FastAPI
from api.v1.api import api_router
import uvicorn


app = FastAPI()

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)