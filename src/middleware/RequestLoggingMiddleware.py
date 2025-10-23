from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from time import time, strftime, gmtime
from enums.DataBaseEnum import DataBaseEnum
from services.SecurityService import SecurityService
from models.LogEntry import LogEntry



class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time()
        response = await call_next(request)
        process_time = (time() - start_time) * 1000 # in milliseconds

        # extract JWT token from authorization header to get user info
        user_data = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            security_service = SecurityService()
            user_data = security_service.verify_access_token(token)

        log_entry = LogEntry(
            timestamp=strftime("%Y-%m-%dT%H:%M:%SZ", gmtime()),
            endpoint=request.url.path,
            status=response.status_code,
            process_time=float(process_time),
            user=user_data.get("username") if user_data else None,
            user_id=user_data.get("id") if user_data else None
        )

        db_client = request.app.db_client
        logs_collection = db_client[DataBaseEnum.LOGS_COLLECTION_NAME.value]

        await logs_collection.insert_one(log_entry.dict(exclude={"id"}))
        return response




        