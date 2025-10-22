from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from contextlib import asynccontextmanager
from fastapi import FastAPI
from controllers.ApplicationUserController import auth_router
from controllers.GenAIController import genai_router
from controllers.ClientController import client_router
from controllers.ContractController import contract_router

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    yield

    app.mongo_conn.close()

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(genai_router)
app.include_router(client_router)
app.include_router(contract_router)
