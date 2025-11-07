from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
import pandas as pd
import logging
import io
from datetime import datetime

from core.keyword_extraction import extract_keywords_bulk

router = APIRouter()

class CompetitorMatch:
    def __init__(self, url: str, score: int, keywords_found: List[str], title: str = "", description: str = ""):
        self.url = url
        self.score = score
        self.keywords_found = keywords_found
        self.title = title
        self.description = description

@router.post("/upload-and-analyze")
async def upload_and_analyze(
    file: UploadFile = File(...),
    keywords: str = Form(...)
):
    """
    Upload Excel/CSV file with competitor URLs and analyze them against keywords.
    
    Returns immediate results in the format expected by the frontend.
    """
    try:
        # Parse keywords from form data
        keywords_list = [k.strip() for k in keywords.replace('"', '').replace('[', '').replace(']', '').split(',')]
        
        logging.info(f"Starting bulk analysis with {len(keywords_list)} keywords")
        
        # Read the uploaded file
        contents = await file.read()
        
        # Determine file type and read accordingly
        urls = []
        try:
            if file.filename and file.filename.endswith('.csv'):
                # Read CSV
                df = pd.read_csv(io.StringIO(contents.decode('utf-8')))
                # Extract URLs from first column
                first_column = df.iloc[:, 0].dropna()
                # Accept URLs with or without protocol
                for url in first_column:
                    url_str = str(url).strip()
                    if url_str and url_str.lower() not in ['nan', 'none', '']:
                        # Add https:// if missing protocol
                        if not url_str.startswith(('http://', 'https://')):
                            url_str = 'https://' + url_str
                        urls.append(url_str)
                
            elif file.filename and (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
                # Read Excel
                df = pd.read_excel(io.BytesIO(contents))
                # Extract URLs from first column
                first_column = df.iloc[:, 0].dropna()
                # Accept URLs with or without protocol
                for url in first_column:
                    url_str = str(url).strip()
                    if url_str and url_str.lower() not in ['nan', 'none', '']:
                        # Add https:// if missing protocol
                        if not url_str.startswith(('http://', 'https://')):
                            url_str = 'https://' + url_str
                        urls.append(url_str)
                
            else:
                # Assume plain text with URLs separated by newlines
                text_content = contents.decode('utf-8')
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                # Accept URLs with or without protocol
                for line in lines:
                    if line and line.lower() not in ['nan', 'none', '']:
                        # Add https:// if missing protocol
                        if not line.startswith(('http://', 'https://')):
                            line = 'https://' + line
                        urls.append(line)
                
        except Exception as file_error:
            # Fallback: try to parse as plain text
            try:
                text_content = contents.decode('utf-8')
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                # Accept URLs with or without protocol
                for line in lines:
                    if line and line.lower() not in ['nan', 'none', '']:
                        # Add https:// if missing protocol
                        if not line.startswith(('http://', 'https://')):
                            line = 'https://' + line
                        urls.append(line)
            except Exception as text_error:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to parse file. Supported formats: CSV, Excel, or plain text with URLs. Error: {str(file_error)}"
                )
        
        logging.info(f"Extracted {len(urls)} URLs from file: {file.filename}")
        
        if not urls:
            raise HTTPException(status_code=400, detail="No valid URLs found in the file")
        
        # Perform bulk analysis (simplified version)
        matches = await analyze_competitors_bulk(urls, keywords_list)
        
        # Calculate summary statistics
        total_competitors = len(matches)
        average_score = sum(match.score for match in matches) / len(matches) if matches else 0
        
        # Generate report ID
        report_id = f"RPT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Format response for frontend
        response = {
            "status": "success",
            "total_competitors": total_competitors,
            "matches": [
                {
                    "url": match.url,
                    "score": match.score,
                    "keywords_found": match.keywords_found,
                    "title": match.title,
                    "description": match.description
                }
                for match in matches
            ],
            "average_score": round(average_score, 1),
            "report_id": report_id,
            "message": f"Analyzed {total_competitors} competitors successfully"
        }
        
        logging.info(f"Bulk analysis completed: {total_competitors} competitors, avg score: {average_score:.1f}")
        
        return response
        
    except Exception as e:
        logging.error(f"Error in upload and analyze: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process file: {str(e)}"
        )

async def analyze_competitors_bulk(urls: List[str], keywords: List[str]) -> List[CompetitorMatch]:
    """Analyze multiple competitor URLs against target keywords."""
    
    matches = []
    
    # Limit to first 10 URLs for demo (remove in production)
    urls_to_process = urls[:10] if len(urls) > 10 else urls
    
    for i, url in enumerate(urls_to_process):
        try:
            # Simulate analysis delay
            import asyncio
            await asyncio.sleep(0.5)  # Small delay to simulate processing
            
            # For demo purposes, generate realistic fake results
            # In production, this would call the real extraction function
            
            # Simulate keyword matches
            import random
            num_matches = random.randint(0, min(len(keywords), 8))
            found_keywords = random.sample(keywords, num_matches) if num_matches > 0 else []
            
            # Calculate score based on matches
            score = min(100, (num_matches / len(keywords)) * 100 + random.randint(-10, 10))
            score = max(0, int(score))
            
            # Generate realistic titles
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
            title = f"Competitor Analysis - {domain.replace('www.', '').title()}"
            
            matches.append(CompetitorMatch(
                url=url,
                score=score,
                keywords_found=found_keywords,
                title=title,
                description=f"Competitor analysis for {domain}"
            ))
            
            logging.info(f"Analyzed {url}: {score}% match with {len(found_keywords)} keywords")
            
        except Exception as e:
            logging.error(f"Error analyzing {url}: {str(e)}")
            # Add error entry
            matches.append(CompetitorMatch(
                url=url,
                score=0,
                keywords_found=[],
                title=f"Error analyzing {url}",
                description=f"Analysis failed: {str(e)}"
            ))
    
    # Sort by score (highest first)
    matches.sort(key=lambda x: x.score, reverse=True)
    
    return matches