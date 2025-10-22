import PyPDF2
from helpers.config import get_settings
from openai import OpenAI
from fastapi import UploadFile
from io import BytesIO
import json

settings = get_settings()


class GenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def analyze_pdf(self, file: UploadFile) -> dict:
        if file.content_type != "application/pdf":
            raise ValueError("Invalid file type. Only PDF files are supported.")
        
        content = await file.read()

        text = self.extract_text_from_pdf(content)

        response = self.client.chat.completions.create(
            model=settings.GENERATION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": f"""Analyze this contract and extract all clauses. 
                    Return only a JSON object where keys are clause names and values are their contents.
                    Contract:\n{text}"""
                }
            ]
        )

        clauses = json.loads(response.choices[0].message.content)
        return clauses
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        text = ""
        pdf_file = BytesIO(file_content)
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            text += page.extract_text()
        return text
    
    async def evaluate_clauses(self, clauses: dict) -> dict:
        
        prompt = (
            "You will be given a JSON object with contract clauses (keys = clause names, values = clause texts). "
            "Assess the contract and return ONLY a JSON object with two keys: \"approved\" (true or false) and \"reasoning\" (a short explanation). "
            "Be concise.\n\nContract clauses JSON:\n"
            + json.dumps(clauses, ensure_ascii=False)
        )

        response = self.client.chat.completions.create(
            model=settings.GENERATION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw_result = response.choices[0].message.content
        result = json.loads(raw_result)
        
        return result
