from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import asyncio
from datetime import datetime

from core.scraping import bulk_scraper

router = APIRouter()

# In-memory storage for analysis results (in production, use Redis or database)
analysis_results = {}
analysis_status = {}

class AnalyzeBulkRequest(BaseModel):
    sites_data: List[Dict[str, Any]]
    target_keywords: List[str]
    client_url: Optional[str] = None  # URL of the client site for sector analysis
    analysis_id: Optional[str] = None

class AnalyzeBulkResponse(BaseModel):
    analysis_id: str
    status: str
    total_sites: int
    target_keywords: List[str]
    message: str

class AnalysisResultsResponse(BaseModel):
    analysis_id: str
    status: str
    progress: Dict[str, Any]
    results: List[Dict[str, Any]]
    summary: Dict[str, Any]

@router.post("/analyze-bulk", response_model=AnalyzeBulkResponse)
async def analyze_bulk(request: AnalyzeBulkRequest, background_tasks: BackgroundTasks):
    """
    Start bulk analysis of competitor sites for keyword matching.
    
    This endpoint accepts a list of sites and target keywords, then processes
    them asynchronously. Use the returned analysis_id to check progress and results.
    """
    try:
        # Generate analysis ID
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(request.sites_data)}"
        
        # Validate input
        if not request.sites_data:
            raise HTTPException(status_code=400, detail="No sites provided for analysis")
        
        if not request.target_keywords:
            raise HTTPException(status_code=400, detail="No target keywords provided")
        
        # Initialize analysis status
        analysis_status[analysis_id] = {
            'status': 'started',
            'total_sites': len(request.sites_data),
            'processed_sites': 0,
            'start_time': datetime.now().isoformat(),
            'target_keywords': request.target_keywords
        }
        
        # Start background analysis
        background_tasks.add_task(
            run_bulk_analysis,
            analysis_id,
            request.sites_data,
            request.target_keywords,
            request.client_url
        )
        
        logging.info(f"Started bulk analysis {analysis_id} for {len(request.sites_data)} sites")
        
        return AnalyzeBulkResponse(
            analysis_id=analysis_id,
            status="started",
            total_sites=len(request.sites_data),
            target_keywords=request.target_keywords,
            message=f"Analysis started. Use GET /api/analyze-bulk/{analysis_id} to check progress."
        )
        
    except Exception as e:
        logging.error(f"Error starting bulk analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start analysis: {str(e)}"
        )

@router.get("/analyze-bulk/{analysis_id}", response_model=AnalysisResultsResponse)
async def get_analysis_results(analysis_id: str):
    """
    Get the results and status of a bulk analysis.
    
    Returns current progress and results (if completed) for the specified analysis.
    """
    try:
        if analysis_id not in analysis_status:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        status_info = analysis_status[analysis_id]
        results = analysis_results.get(analysis_id, [])
        
        # Calculate summary statistics
        summary = calculate_analysis_summary(results, status_info)
        
        return AnalysisResultsResponse(
            analysis_id=analysis_id,
            status=status_info['status'],
            progress={
                'total_sites': status_info['total_sites'],
                'processed_sites': status_info['processed_sites'],
                'start_time': status_info['start_time'],
                'end_time': status_info.get('end_time'),
                'duration': status_info.get('duration_seconds')
            },
            results=results,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error retrieving analysis results {analysis_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve results: {str(e)}"
        )

@router.get("/analyze-bulk")
async def list_analyses():
    """List all analysis sessions with their current status."""
    try:
        analyses_list = []
        
        for analysis_id, status_info in analysis_status.items():
            analyses_list.append({
                'analysis_id': analysis_id,
                'status': status_info['status'],
                'total_sites': status_info['total_sites'],
                'processed_sites': status_info['processed_sites'],
                'start_time': status_info['start_time'],
                'target_keywords_count': len(status_info['target_keywords'])
            })
        
        # Sort by start time (most recent first)
        analyses_list.sort(key=lambda x: x['start_time'], reverse=True)
        
        return {
            'total_analyses': len(analyses_list),
            'analyses': analyses_list
        }
        
    except Exception as e:
        logging.error(f"Error listing analyses: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list analyses: {str(e)}"
        )

@router.delete("/analyze-bulk/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete a specific analysis from memory. Supports partial ID matching."""
    try:
        # Try exact match first
        if analysis_id in analysis_status:
            target_id = analysis_id
        else:
            # Try to find ID that contains the provided ID (for legacy formats)
            matching_ids = [aid for aid in analysis_status.keys() if analysis_id in aid or aid in analysis_id]
            if not matching_ids:
                logging.warning(f"Analysis not found: {analysis_id}. Available IDs: {list(analysis_status.keys())}")
                raise HTTPException(status_code=404, detail=f"Analysis not found: {analysis_id}")
            target_id = matching_ids[0]
            logging.info(f"Found matching analysis: {target_id} for request: {analysis_id}")
        
        # Remove from both dictionaries
        del analysis_status[target_id]
        if target_id in analysis_results:
            del analysis_results[target_id]
        
        logging.info(f"Deleted analysis {target_id}")
        
        return {
            'status': 'success',
            'message': f'Analysis {target_id} deleted successfully',
            'deleted_id': target_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting analysis {analysis_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete analysis: {str(e)}"
        )

@router.delete("/analyze-bulk")
async def cleanup_old_analyses(days_old: int = 7, status_filter: str = None):
    """
    Delete old analyses from memory.
    
    - days_old: Delete analyses older than N days (default: 7)
    - status_filter: Only delete analyses with specific status (optional: 'completed', 'error', 'started')
    """
    try:
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        deleted_ids = []
        
        for analysis_id, status_info in list(analysis_status.items()):
            # Check if analysis is old enough
            start_time = datetime.fromisoformat(status_info['start_time'])
            
            # Apply filters
            should_delete = start_time < cutoff_date
            
            if status_filter:
                should_delete = should_delete and status_info['status'] == status_filter
            
            if should_delete:
                # Remove from both dictionaries
                del analysis_status[analysis_id]
                if analysis_id in analysis_results:
                    del analysis_results[analysis_id]
                deleted_ids.append(analysis_id)
        
        logging.info(f"Cleaned up {len(deleted_ids)} old analyses")
        
        return {
            'status': 'success',
            'deleted_count': len(deleted_ids),
            'deleted_ids': deleted_ids,
            'remaining_analyses': len(analysis_status)
        }
        
    except Exception as e:
        logging.error(f"Error cleaning up analyses: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cleanup analyses: {str(e)}"
        )

async def run_bulk_analysis(analysis_id: str, sites_data: List[Dict], target_keywords: List[str], client_url: str = None):
    """Background task to run the actual bulk analysis with sector relevance."""
    try:
        # Update status to processing
        analysis_status[analysis_id]['status'] = 'processing'
        
        # Run the bulk scraping with sector analysis
        results = await bulk_scraper.analyze_sites_bulk(sites_data, target_keywords, client_url)
        
        # Store results
        analysis_results[analysis_id] = results
        
        # Update final status
        end_time = datetime.now()
        start_time = datetime.fromisoformat(analysis_status[analysis_id]['start_time'])
        duration = (end_time - start_time).total_seconds()
        
        analysis_status[analysis_id].update({
            'status': 'completed',
            'processed_sites': len(results),
            'end_time': end_time.isoformat(),
            'duration_seconds': round(duration, 2)
        })
        
        logging.info(f"Completed bulk analysis {analysis_id} in {duration:.2f} seconds")
        
    except Exception as e:
        logging.error(f"Error in bulk analysis {analysis_id}: {str(e)}")
        analysis_status[analysis_id].update({
            'status': 'error',
            'error_message': str(e),
            'end_time': datetime.now().isoformat()
        })

def calculate_analysis_summary(results: List[Dict], status_info: Dict) -> Dict[str, Any]:
    """Calculate summary statistics for analysis results."""
    if not results:
        return {
            'total_sites': status_info['total_sites'],
            'sites_with_matches': 0,
            'sites_processed': 0,
            'average_score': 0,
            'top_score': 0,
            'keywords_found': [],
            'error_count': 0
        }
    
    # Calculate statistics
    sites_with_matches = len([r for r in results if r.get('match_score', 0) > 0])
    scores = [r.get('match_score', 0) for r in results]
    average_score = sum(scores) / len(scores) if scores else 0
    top_score = max(scores) if scores else 0
    error_count = len([r for r in results if r.get('status') == 'error'])
    
    # Collect all found keywords
    all_keywords = set()
    for result in results:
        all_keywords.update(result.get('found_keywords', []))
    
    return {
        'total_sites': len(results),
        'sites_with_matches': sites_with_matches,
        'sites_processed': len(results),
        'average_score': round(average_score, 1),
        'top_score': round(top_score, 1),
        'keywords_found': list(all_keywords),
        'error_count': error_count
    }