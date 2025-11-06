from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

from utils.excel_utils import excel_processor

router = APIRouter()

class UploadFileResponse(BaseModel):
    filename: str
    total_sites: int
    sites_data: List[Dict[str, Any]]
    status: str

@router.post("/upload-file", response_model=UploadFileResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload Excel file containing competitor URLs.
    
    Expected Excel format:
    - Required column: "URL" 
    - Optional columns: "Nome azienda", "Codice ATECO"
    
    Returns processed site data ready for bulk analysis.
    """
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail="Only Excel files (.xlsx, .xls) are supported"
            )
        
        # Read file content
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty"
            )
        
        logging.info(f"Processing uploaded file: {file.filename}")
        
        # Process Excel file
        sites_data = excel_processor.process_excel_file(file_content, file.filename)
        
        if len(sites_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="No valid URLs found in the Excel file"
            )
        
        return UploadFileResponse(
            filename=file.filename,
            total_sites=len(sites_data),
            sites_data=sites_data,
            status="success"
        )
        
    except ValueError as e:
        logging.error(f"Validation error processing {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logging.error(f"Unexpected error processing {file.filename}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file: {str(e)}"
        )

@router.get("/sample-excel")
async def download_sample_excel():
    """
    Download a sample Excel file showing the expected format.
    """
    try:
        sample_content = excel_processor.create_sample_excel()
        
        return Response(
            content=sample_content,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=sample_competitors.xlsx"}
        )
    except Exception as e:
        logging.error(f"Error creating sample Excel: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate sample file"
        )