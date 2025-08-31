from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class KeywordExtractionRequest(BaseModel):
    text: str
    schema: str
    examples: Optional[List[str]] = None

class KeywordExtractionResponse(BaseModel):
    keywords: str

class AssessmentRequest(BaseModel):
    keywords: str

class AssessmentResponse(BaseModel):
    assessment: str

class ResumeUploadResponse(BaseModel):
    message: str
    files_processed: int
    vector_store_created: bool

class CandidateAnalysisRequest(BaseModel):
    question: Optional[str] = None

class CandidateAnalysisResponse(BaseModel):
    keywords: str
    assessment: str

class HealthResponse(BaseModel):
    status: str
    message: str
