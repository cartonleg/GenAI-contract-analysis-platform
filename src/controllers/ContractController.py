from fastapi import APIRouter, UploadFile, Request, Depends
from fastapi.responses import JSONResponse
from services.ContractService import ContractService
from services.GenAIService import GenAIService
from services.ClientService import ClientService
from bson import ObjectId
from dependencies.auth import verify_jwt

contract_router = APIRouter(prefix="/contracts")

@contract_router.post("/")
async def create_contract(request: Request, title: str, content: UploadFile, client: str, user_data: dict = Depends(verify_jwt)):
    contract_service = ContractService(db_client=request.app.db_client)
    client_service = ClientService(db_client=request.app.db_client)
    client_object = await client_service.get_client_by_name(client)
    client_id = client_object.id if client_object else None

    contract = await contract_service.create_contract_record(
        title=title,
        content=content,
        application_user_id=ObjectId(user_data.get("id")),
        client_id=client_id
    )

    if not contract:
        raise JSONResponse(status_code=400, content={"detail": "Contract with this title already exists"})

    return JSONResponse(status_code=201, content={"message": "Contract created successfully", "contract_id": str(contract["_id"])})

@contract_router.get("/{contract_title}")
async def get_contract(contract_title: str, request: Request):
    contract_service = ContractService(db_client=request.app.db_client)
    contract = await contract_service.get_contract_by_title(contract_title)

    if not contract:
        return JSONResponse(status_code=404, content={"detail": "Contract not found"})

    contract["_id"] = str(contract["_id"])
    contract["application_user_id"] = str(contract["application_user_id"])
    contract["client_id"] = str(contract["client_id"])
    del contract["content"]

    return JSONResponse(status_code=200, content=contract)

@contract_router.put("/{contract_title}")
async def update_contract(contract_title: str, request: Request, title: str = None, content: UploadFile = None, client: str = None):
    contract_service = ContractService(db_client=request.app.db_client)
    client_service = ClientService(db_client=request.app.db_client)

    contract = await contract_service.get_contract_by_title(contract_title)
    if not contract:
        return JSONResponse(status_code=404, content={"detail": "Contract not found"})
    contract_id = contract["_id"]

    client_id = None
    if client:
        client_obj = await client_service.get_client_by_name(client)
        client_id = client_obj.id if client_obj else None

    updated_contract = await contract_service.update_contract_record(
        ObjectId(contract_id),
        title=title,
        content=content,
        client_id=ObjectId(client_id) if client_id else None
    )

    if not updated_contract:
        return JSONResponse(status_code=404, content={"detail": "Contract not found or no changes made"})
   
    updated_contract["_id"] = str(updated_contract["_id"])
    updated_contract["application_user_id"] = str(updated_contract["application_user_id"])
    updated_contract["client_id"] = str(updated_contract["client_id"])
    del updated_contract["content"]

    return JSONResponse(status_code=200, content=updated_contract)

@contract_router.delete("/{contract_title}")
async def delete_contract(contract_title: str, request: Request):
    contract_service = ContractService(db_client=request.app.db_client)
    success = await contract_service.delete_contract_record(contract_title)

    if not success:
        return JSONResponse(status_code=404, content={"detail": "Contract not found"})

    return JSONResponse(status_code=200, content={"message": "Contract deleted successfully"})


@contract_router.post("/{contract_title}/init-genai")
async def init_genai_for_contract(request: Request,contract_title: str, user_data: dict = Depends(verify_jwt)):
    genai_service = GenAIService(request=request)
    contract_service = ContractService(db_client=request.app.db_client)

    contract = await contract_service.get_contract_by_title(contract_title)

    if not contract:
        return JSONResponse(status_code=404, content={"message": "Contract not found"})

    await genai_service.analyze_and_evaluate_pdf(binary_content=contract["content"], contract_id=contract["_id"])

    return JSONResponse(status_code=200, content={"message": "GenAI analysis and evaluation completed successfully, recheck the contract record for clauses and evaluation, if they don't appear give it a while."})

