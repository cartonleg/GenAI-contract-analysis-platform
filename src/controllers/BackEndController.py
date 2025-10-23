from fastapi import APIRouter, Request, Depends
from dependencies.auth import verify_jwt
from fastapi.responses import JSONResponse

backend_router = APIRouter()

@backend_router.get("/healthz")
async def health_check():
    return {"status": "ok"}

@backend_router.get("/readyz")
async def readiness_check(request: Request):
    mongo_conn = request.app.mongo_conn
    
    try:
        await mongo_conn.admin.command('ping')
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}
    
@backend_router.get("/logs")
async def get_logs(request: Request, endpoint: str = None, user: str = None, date: str = None, status: int = None, user_data: dict = Depends(verify_jwt)):
    if user_data["role"] != "admin":
        return JSONResponse(content={"error": "Unauthorized"}, status_code=403)
    
    db_client = request.app.db_client
    logs_collection = db_client["logs"]

    query = {}
    if endpoint:
        query["endpoint"] = endpoint
    if user:
        query["user"] = user
    if date:
        query["timestamp"] = {"$regex": f"^{date}"}
    if status:
        query["status"] = status

    logs_cursor = logs_collection.find(query)
    logs = []
    async for log in logs_cursor:
        log["_id"] = str(log["_id"])  # Convert ObjectId to string for JSON serialization
        logs.append(log)

    return {"logs": logs}