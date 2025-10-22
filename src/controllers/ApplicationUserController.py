from fastapi import APIRouter, Request
from services.ApplicationUserService import ApplicationUserService
from .schemes.RegisterRequest import RegisterRequest
from .schemes.LoginRequest import LoginRequest
from fastapi.responses import JSONResponse
from services.SecurityService import SecurityService

auth_router = APIRouter(prefix="/auth")

@auth_router.post("/register")
async def register(request: Request, register_request: RegisterRequest):
    application_user_service = ApplicationUserService(request.app.db_client)
    application_user = await application_user_service.create_application_user(
        username=register_request.username,
        password=register_request.password,
        role=register_request.role
    )
    if application_user is None:
        return JSONResponse(
            status_code=400,
            content={"message": "Username already exists"}
        )
    return JSONResponse(
        status_code=201,
        content={"message": "User registered successfully"}
    )

@auth_router.post("/login")
async def login(request: Request, login_request: LoginRequest):
    application_user_service = ApplicationUserService(request.app.db_client)
    security_service = SecurityService()
    application_user = await application_user_service.authenticate_application_user(
        username=login_request.username,
        password=login_request.password
    )
    if not application_user:
        return JSONResponse(
            status_code=401,
            content={"message": "Invalid username or password"}
        )

    access_token = security_service.create_access_token(username=application_user.username, role=application_user.role)
    return JSONResponse(
        status_code=200,
        content={"access_token": access_token, "token_type": "bearer"})
    