"""
LLM Guard API - FastAPI application for input and output scanning
Deployable on Vercel with serverless functions
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from llm_guard import scan_output, scan_prompt
from llm_guard.input_scanners import PromptInjection, Secrets
from llm_guard.input_scanners.prompt_injection import MatchType 
from llm_guard.output_scanners import NoRefusal, Relevance

app = FastAPI(
    title="LLM Guard API",
    description="API for scanning prompts and responses using LLM Guard",
    version="1.0.0"
)

# Initialize scanners (will be loaded once per serverless function)
input_scanners = [
    PromptInjection(threshold=0.5, match_type=MatchType.FULL),
    Secrets(),
]

output_scanners = [
    NoRefusal(),
    Relevance()
]

class InputScanRequest(BaseModel):
    prompt: str
    user_id: Optional[str] = None

class InputScanResponse(BaseModel):
    sanitized_prompt: str
    is_valid: bool
    scores: Dict[str, float]
    blocked_reasons: list

class OutputScanRequest(BaseModel):
    prompt: str
    response: str
    user_id: Optional[str] = None

class OutputScanResponse(BaseModel):
    sanitized_response: str
    is_valid: bool
    scores: Dict[str, float]
    blocked_reasons: list

@app.get("/")
async def root():
    return {"message": "LLM Guard API is running"}

@app.post("/scan-input", response_model=InputScanResponse)
async def scan_input(request: InputScanRequest):
    """
    Scan and validate input prompts
    """
    try:
        sanitized_prompt, results_valid, results_score = scan_prompt(
            input_scanners, request.prompt
        )
        
        # Check which scanners failed
        blocked_reasons = []
        for scanner_name, is_valid in results_valid.items():
            if not is_valid:
                blocked_reasons.append(f"{scanner_name}: {results_score.get(scanner_name, 'N/A')}")
        
        return InputScanResponse(
            sanitized_prompt=sanitized_prompt,
            is_valid=all(results_valid.values()),
            scores=results_score,
            blocked_reasons=blocked_reasons
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scanning error: {str(e)}")

@app.post("/scan-output", response_model=OutputScanResponse)
async def scan_output_endpoint(request: OutputScanRequest):
    """
    Scan and validate AI responses
    """
    try:
        sanitized_response, results_valid, results_score = scan_output(
            output_scanners, request.prompt, request.response
        )
        
        # Check which scanners failed
        blocked_reasons = []
        for scanner_name, is_valid in results_valid.items():
            if not is_valid:
                blocked_reasons.append(f"{scanner_name}: {results_score.get(scanner_name, 'N/A')}")
        
        return OutputScanResponse(
            sanitized_response=sanitized_response,
            is_valid=all(results_valid.values()),
            scores=results_score,
            blocked_reasons=blocked_reasons
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scanning error: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "scanners_loaded": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 