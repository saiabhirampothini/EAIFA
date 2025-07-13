from fastapi import FastAPI
from interfaces.api.routes import router

app = FastAPI()
app.include_router(router)
