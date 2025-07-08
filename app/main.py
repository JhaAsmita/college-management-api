from fastapi import FastAPI
from app import models
from app.database import engine
from app.routes import router

app = FastAPI()

models.Base.metadata.create_all(bind=engine)
app.include_router(router)
