from fastapi import FastAPI
from app.routers.api_routers import router
app: FastAPI = FastAPI(title='FastAPI')

app.include_router(router, prefix="/api")
