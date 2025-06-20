# ai/app.py
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agent import process_html_to_lcnc
from typing import Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="HTML to LCNC Converter",
    description="Converts HTML/CSS to Low-Code/No-Code components using LLM-powered agents",
    version="1.0.0"
)

class ConversionRequest(BaseModel):
    """Request model for HTML/CSS conversion"""
    html_content: str
    css_content: str

class ConversionResponse(BaseModel):
    """Response model for conversion results"""
    status: str
    lcnc_structure: Union[list, dict]
    analysis_report: dict
    error: Optional[str] = None

@app.post("/convert", response_model=ConversionResponse)
async def convert_html_to_lcnc(request: ConversionRequest) -> ConversionResponse:
    """Convert HTML/CSS to LCNC components"""
    try:
        # Process the conversion
        result = process_html_to_lcnc(
            html_content=request.html_content,
            css_content=request.css_content
        )
        
        # Check for errors
        if result.get("error"):
            return ConversionResponse(
                status="error",
                lcnc_structure=[],
                analysis_report={},
                error=result["error"]
            )
        
        # Return successful response
        return ConversionResponse(
            status="success",
            lcnc_structure=result.get("lcnc_structure", []),
            analysis_report=result.get("analysis_report", {}),
            error=None
        )
        
    except Exception as e:
        logger.error(f"Error processing conversion request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {"status": "healthy"}