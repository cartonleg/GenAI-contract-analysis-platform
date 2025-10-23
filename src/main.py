from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from contextlib import asynccontextmanager
from fastapi import FastAPI
from controllers.ApplicationUserController import auth_router
from controllers.GenAIController import genai_router
from controllers.ClientController import client_router
from controllers.ContractController import contract_router
from controllers.BackEndController import backend_router
from middleware.RequestLoggingMiddleware import RequestLoggingMiddleware

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    yield

    app.mongo_conn.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(RequestLoggingMiddleware)

app.include_router(auth_router)
app.include_router(genai_router)
app.include_router(client_router)
app.include_router(contract_router)
app.include_router(backend_router)
