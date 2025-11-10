"""
🆕 API Endpoints for Analysis Management
Allows frontend to list, retrieve, and reconnect to analyses
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional, Literal
import logging
import json

from api.analysis_manager import (
    list_all_analyses,
    get_analysis_status,
)

router = APIRouter()

@router.get("/api/analyses")
async def list_analyses(
    status: Optional[Literal["in_progress", "completed", "failed"]] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Max number of analyses to return")
):
    """
    📋 List all analyses with optional filtering
    
    Query params:
    - status: Filter by 'in_progress', 'completed', or 'failed' (optional)
    - limit: Max number of results (default: 50, max: 100)
    
    Returns:
    {
        "analyses": [
            {
                "id": "20251110_143022",
                "status": "in_progress",
                "client_url": "bulk_analysis",
                "total_sites": 50,
                "processed_sites": 23,
                "progress": 46,
                "started_at": "2025-11-10T14:30:22",
                "completed_at": null
            },
            ...
        ],
        "stats": {
            "total": 10,
            "in_progress": 2,
            "completed": 7,
            "failed": 1
        }
    }
    """
    try:
        result = list_all_analyses(status=status, limit=limit)
        
        if not result:
            return {
                "analyses": [],
                "stats": {
                    "total": 0,
                    "in_progress": 0,
                    "completed": 0,
                    "failed": 0
                }
            }
        
        return result
    
    except Exception as e:
        logging.error(f"❌ Error listing analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing analyses: {str(e)}")


@router.get("/api/analyses/{analysis_id}")
async def get_analysis(analysis_id: str):
    """
    📊 Get detailed information about a specific analysis
    
    Returns full analysis data including all results:
    {
        "metadata": {
            "id": "20251110_143022",
            "status": "completed",
            "client_url": "bulk_analysis",
            "total_sites": 50,
            "processed_sites": 50,
            "progress": 100,
            "started_at": "2025-11-10T14:30:22",
            "completed_at": "2025-11-10T14:45:30"
        },
        "results": [
            {
                "url": "https://example.com",
                "score": 75,
                "keywords_found": [...],
                "title": "...",
                "description": "...",
                "status": {...}
            },
            ...
        ]
    }
    """
    try:
        analysis_data = get_analysis_status(analysis_id)
        
        if not analysis_data:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis {analysis_id} not found"
            )
        
        return analysis_data
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ Error retrieving analysis {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving analysis: {str(e)}")


@router.get("/api/analyses/{analysis_id}/stream")
async def reconnect_to_analysis_stream(analysis_id: str):
    """
    🔄 Reconnect to an ongoing analysis stream
    
    If analysis is 'in_progress', returns SSE stream with current progress.
    If analysis is 'completed', returns final results immediately.
    If analysis is 'failed', returns error event.
    
    Event format (SSE):
    data: {"event": "reconnected", "analysis_id": "...", "current_progress": 45, "total": 50}
    data: {"event": "progress", "url": "...", "current": 46, "total": 50}
    data: {"event": "result", "url": "...", "score": 75}
    data: {"event": "complete", "matches": [...]}
    """
    try:
        analysis_data = get_analysis_status(analysis_id)
        
        if not analysis_data:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis {analysis_id} not found"
            )
        
        metadata = analysis_data['metadata']
        status = metadata['status']
        
        # Create SSE stream
        async def event_generator():
            if status == 'completed':
                # Analysis already finished - send complete event immediately
                yield f"data: {json.dumps({'event': 'reconnected', 'status': 'completed', 'message': 'Analisi già completata'})}\n\n"
                
                # Send final results
                final_response = {
                    "event": "complete",
                    "status": "success",
                    "total_competitors": len(analysis_data['results']),
                    "matches": analysis_data['results'],
                    "metadata": metadata
                }
                yield f"data: {json.dumps(final_response)}\n\n"
                
            elif status == 'failed':
                # Analysis failed - send error event
                yield f"data: {json.dumps({'event': 'error', 'status': 'failed', 'message': metadata.get('error_message', 'Analisi fallita')})}\n\n"
                
            elif status == 'in_progress':
                # Analysis still running - send current progress
                processed = metadata['processed_sites']
                total = metadata['total_sites']
                
                yield f"data: {json.dumps({'event': 'reconnected', 'status': 'in_progress', 'current': processed, 'total': total, 'progress': metadata['progress'], 'message': f'Riconnesso: {processed}/{total} siti analizzati'})}\n\n"
                
                # Send already completed results
                for result in analysis_data['results']:
                    yield f"data: {json.dumps({'event': 'result', 'url': result['url'], 'score': result['score'], 'keywords_found': result['keywords_found'], 'title': result['title']})}\n\n"
                
                # Note: Real-time updates would require WebSocket or polling
                # For now, just send what we have
                yield f"data: {json.dumps({'event': 'info', 'message': 'Stream terminato. Aggiorna la pagina per vedere i progressi più recenti.'})}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ Error reconnecting to analysis {analysis_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error reconnecting to analysis: {str(e)}")
