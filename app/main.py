from fastapi import FastAPI
from app.routes import router

app = FastAPI(title="College Management API")
app.include_router(router)
