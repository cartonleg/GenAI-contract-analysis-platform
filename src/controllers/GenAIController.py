from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.GenAIService import GenAIService
from services.SecurityService import SecurityService
from .schemes.EvaluateRequest import EvaluateRequest
from dependencies.auth import verify_jwt

genai_router = APIRouter(prefix="/genai")

@genai_router.post("/analyze-contract")
async def analyze_contract(file: UploadFile = File(...), user_data: dict = Depends(verify_jwt)):
    try:
        genai_service = GenAIService()
        clauses = await genai_service.analyze_pdf(file)
        return JSONResponse(status_code=200, content=clauses)
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"error analyzing contract: {str(e)}"})

@genai_router.post("/evaluate-contract")
async def evaluate_contract(clauses: EvaluateRequest, user_data: dict = Depends(verify_jwt)):
    try:
        genai_service = GenAIService()
        evaluation = await genai_service.evaluate_clauses(clauses.clauses)
        return JSONResponse(status_code=200, content=evaluation)
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"error evaluating contract: {str(e)}"})