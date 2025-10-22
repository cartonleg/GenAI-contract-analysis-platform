from pydantic import BaseModel
from typing import Dict, Any

class EvaluateRequest(BaseModel):
    clauses: Dict[str, Any]
    