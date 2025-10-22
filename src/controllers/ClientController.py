from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from services.ClientService import ClientService
from services.ContractService import ContractService
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

@client_router.get("/{client_name}/contracts")
async def get_contracts_by_client_name(client_name: str, request: Request, user_data: dict = Depends(verify_jwt)):
    client_service = ClientService(db_client=request.app.db_client)
    contract_service = ContractService(db_client=request.app.db_client)

    client = await client_service.get_client_by_name(client_name)
    if not client:
        return JSONResponse(status_code=404, content={"error": "Client not found"})

    contracts = await contract_service.get_all_contracts_with_client_id(client.id)

    return JSONResponse(status_code=200, content={"client_name": client_name, "contracts": contracts})