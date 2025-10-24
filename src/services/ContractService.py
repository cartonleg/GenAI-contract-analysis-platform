from motor.motor_asyncio import AsyncIOMotorClient
from enums.DataBaseEnum import DataBaseEnum
from fastapi import UploadFile
from bson import ObjectId, Binary
from models.Contract import Contract

class ContractService:
    def __init__(self, db_client: AsyncIOMotorClient): 
        self.collection = db_client[DataBaseEnum.CONTRACT_COLLECTION_NAME.value]

    async def init_indexes(self):
        """This method is to make sure that the contract title is unique by creating an index on it."""
        await self.collection.create_index("title", unique=True)

    async def get_contract_by_title_and_application_user_id(self, title: str, application_user_id: ObjectId = None):
        contract = await self.collection.find_one({"title": title, "application_user_id": application_user_id})
        if contract:
            return contract
        return None
    
    async def get_contract_by_id(self, contract_id):
        contract = await self.collection.find_one({"_id": contract_id})
        if contract:
            return contract
        return None

    async def create_contract_record(self, title: str, content: UploadFile, application_user_id: ObjectId, client_id: ObjectId = None):
        if await self.get_contract_by_title(title, application_user_id):
            return None
        
        # convert the content to binary, but we have to read it first
        content = await content.read()

        contract = Contract(
            title=title,
            content=Binary(content),
            application_user_id=application_user_id,
            client_id=client_id
        )
        result = await self.collection.insert_one(contract.dict(exclude={"id"}))
        contract._id = result.inserted_id
        return contract

    async def update_contract_record(self, contract_id, title: str = None, content: UploadFile = None, client_id: ObjectId = None, application_user_id: ObjectId = None):
        update_data = {}
        if title:
            update_data["title"] = title
        if content:
            content = await content.read()
            update_data["content"] = Binary(content)
        if client_id:
            update_data["client_id"] = client_id

        if not update_data:
            return None  # Nothing to update

        result = await self.collection.update_one(
            {"_id": contract_id, "application_user_id": application_user_id},
            {"$set": update_data}
        )

        if result.modified_count == 0:
            return None  # No document was updated

        return await self.get_contract_by_id(contract_id)

    async def delete_contract_record(self, contract_title: str, application_user_id: ObjectId):
        result = await self.collection.delete_one({"title": contract_title, "application_user_id": application_user_id})
        return result.deleted_count > 0

    async def get_all_contracts_with_client_id(self, client_id: ObjectId):
        contracts = []
        cursor = self.collection.find({"client_id": client_id})
        async for contract in cursor:
            contracts.append(contract["title"])
        return contracts
    
