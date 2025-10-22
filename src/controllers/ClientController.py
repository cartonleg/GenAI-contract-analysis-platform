from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from services.ClientService import ClientService
from dependencies.auth import verify_jwt
from bson import ObjectId

client_router = APIRouter(prefix="/clients")

@client_router.post("/")
async def create_client_record(request: Request, record_name: str, user_data: dict = Depends(verify_jwt)):
    client_service = ClientService(db_client=request.app.db_client)
    client = await client_service.create_client_record(record_name=record_name, application_user_id=ObjectId(user_data.get("id")))

    if not client:
        return JSONResponse(status_code=400, content={"error": "Client with this name already exists"})

    return JSONResponse(status_code=201, content={"message": "Client created successfully", "client_id": str(client.id)})
