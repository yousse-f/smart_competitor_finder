"""
Report API endpoints for Smart Competitor Finder
Handles report generation and download functionality
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
from datetime import datetime
import asyncio

from core.report_generator import ReportGenerator
from core.scraping import BulkScraper
from core.matching import MatchingEngine

router = APIRouter()

# Global storage for analysis results (in production, use proper database)
analysis_cache = {}


class ReportRequest(BaseModel):
    """Request model for report generation"""
    client_url: str
    keywords: List[str]
    analysis_id: Optional[str] = None  # If we have cached analysis results
    competitors: Optional[List[str]] = None  # Direct competitor URLs


class ReportStatus(BaseModel):
    """Report generation status model"""
    status: str  # "pending", "processing", "completed", "failed"
    message: str
    report_path: Optional[str] = None
    created_at: str


# In-memory storage for report status (use Redis/database in production)
report_status_cache = {}


@router.post("/generate-report")
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate comprehensive analysis report
    
    This endpoint can work in two modes:
    1. Use existing analysis results (if analysis_id provided)
    2. Perform fresh analysis (if competitors list provided)
    """
    try:
        # Generate unique report ID
        report_id = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize report status
        report_status_cache[report_id] = ReportStatus(
            status="pending",
            message="Report generation queued",
            created_at=datetime.now().isoformat()
        )
        
        # Start background report generation
        background_tasks.add_task(
            _generate_report_background,
            report_id,
            request
        )
        
        return {
            "report_id": report_id,
            "status": "pending",
            "message": "Report generation started. Use /api/report-status/{report_id} to check progress."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start report generation: {str(e)}")


@router.get("/report-status/{report_id}")
async def get_report_status(report_id: str):
    """Get the status of report generation"""
    if report_id not in report_status_cache:
        raise HTTPException(status_code=404, detail="Report not found")
    
    status = report_status_cache[report_id]
    return {
        "report_id": report_id,
        "status": status.status,
        "message": status.message,
        "report_path": status.report_path,
        "created_at": status.created_at
    }


@router.get("/download-report/{report_id}")
async def download_report(report_id: str):
    """Download the generated report"""
    if report_id not in report_status_cache:
        raise HTTPException(status_code=404, detail="Report not found")
    
    status = report_status_cache[report_id]
    
    if status.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Report not ready. Current status: {status.status}"
        )
    
    if not status.report_path or not os.path.exists(status.report_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    # Generate a user-friendly filename
    filename = f"competitor_analysis_{report_id}.xlsx"
    
    return FileResponse(
        path=status.report_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.delete("/report/{report_id}")
async def delete_report(report_id: str):
    """Delete a generated report and clean up files"""
    if report_id not in report_status_cache:
        raise HTTPException(status_code=404, detail="Report not found")
    
    status = report_status_cache[report_id]
    
    # Delete file if it exists
    if status.report_path and os.path.exists(status.report_path):
        try:
            os.remove(status.report_path)
        except Exception as e:
            print(f"Warning: Could not delete report file {status.report_path}: {e}")
    
    # Remove from cache
    del report_status_cache[report_id]
    
    return {"message": "Report deleted successfully"}


@router.get("/reports")
async def list_reports():
    """List all available reports"""
    reports = []
    for report_id, status in report_status_cache.items():
        reports.append({
            "report_id": report_id,
            "status": status.status,
            "message": status.message,
            "created_at": status.created_at,
            "has_file": status.report_path and os.path.exists(status.report_path) if status.report_path else False
        })
    
    return {"reports": reports}


async def _generate_report_background(report_id: str, request: ReportRequest):
    """Background task for report generation"""
    try:
        # Update status
        report_status_cache[report_id].status = "processing"
        report_status_cache[report_id].message = "Analyzing competitors and generating report..."
        
        # Get or generate analysis results
        failed_sites = []  # Initialize failed_sites list
        if request.analysis_id and request.analysis_id in analysis_cache:
            # Use cached analysis results
            cached_data = analysis_cache[request.analysis_id]
            if isinstance(cached_data, dict) and 'results' in cached_data:
                analysis_results = cached_data['results']
                failed_sites = cached_data.get('failed_sites', [])
            else:
                analysis_results = cached_data
            print(f"Using cached analysis results for {request.analysis_id}")
        elif request.analysis_id:
            # 🆕 Try to load from JSON file (persistent storage)
            from .analysis_manager import get_analysis_status
            analysis_data = get_analysis_status(request.analysis_id)
            if analysis_data:
                analysis_results = analysis_data.get('results', [])
                failed_sites = analysis_data.get('failed_sites', [])
                print(f"Loaded analysis from JSON: {request.analysis_id}")
            else:
                print(f"Analysis ID not found, performing fresh analysis")
                analysis_results, failed_sites = await _perform_analysis(request)
        else:
            # Perform fresh analysis
            print(f"Performing fresh analysis for {len(request.competitors)} competitors")
            analysis_results, failed_sites = await _perform_analysis(request)
        
        # Generate report
        generator = ReportGenerator()
        
        # Create reports directory
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate report file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"competitor_analysis_{timestamp}.xlsx"
        report_path = os.path.join(reports_dir, report_filename)
        
        final_path = generator.generate_comprehensive_report(
            client_url=request.client_url,
            client_keywords=request.keywords,
            analysis_results=analysis_results,
            output_path=report_path,
            failed_sites=failed_sites  # 🆕 Pass failed sites to report
        )
        
        # Update status
        report_status_cache[report_id].status = "completed"
        report_status_cache[report_id].message = "Report generated successfully"
        report_status_cache[report_id].report_path = final_path
        
        print(f"Report generated successfully: {final_path}")
        
    except Exception as e:
        # Update status with error
        report_status_cache[report_id].status = "failed"
        report_status_cache[report_id].message = f"Report generation failed: {str(e)}"
        print(f"Report generation failed: {e}")


async def _perform_analysis(request: ReportRequest) -> tuple[List[Dict], List[Dict]]:
    """
    Perform competitor analysis
    
    Returns:
        tuple: (processed_results, failed_sites)
    """
    if not request.competitors:
        raise ValueError("No competitors provided for analysis")
    
    # Initialize scraper
    scraper = BulkScraper()
    
    # Prepare site data for bulk analysis
    sites_data = [{'url': url} for url in request.competitors]
    
    # Perform bulk scraping and analysis
    results = await scraper.analyze_sites_bulk(
        sites_data=sites_data,
        target_keywords=request.keywords,
        client_url=request.client_url
    )
    
    # Separate successful and failed results
    processed_results = []
    failed_sites = []
    
    for result in results:
        if result.get('error') or result.get('status') == 'error':
            # Track failed site with detailed error info
            error_msg = result.get('error_message') or result.get('error', 'Unknown error')
            
            # Categorize error and provide suggestion
            suggestion = _get_error_suggestion(error_msg)
            
            failed_sites.append({
                'url': result.get('url', 'Unknown'),
                'error': error_msg,
                'suggestion': suggestion,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'company_name': result.get('company_name', ''),
                'ateco_code': result.get('ateco_code', '')
            })
            
            # Still add to processed results with zero scores for consistency
            processed_results.append({
                'url': result.get('url', 'Unknown'),
                'total_score': 0.0,
                'keyword_score': 0.0,
                'semantic_score': 0.0,
                'sector': 'Unknown',
                'is_relevant': False,
                'keywords_found': [],
                'semantic_similarity': 0.0,
                'relevance_label': 'Analysis Failed',
                'analysis_notes': error_msg,
                'content_summary': 'Analysis failed'
            })
        else:
            # Extract analysis details from bulk analysis result
            score_details = result.get('score_details', {})
            sector_data = result.get('sector_analysis', {})
            semantic_data = result.get('semantic_analysis', {})
            
            processed_results.append({
                'url': result.get('url', 'Unknown'),
                'total_score': result.get('match_score', 0.0) / 100.0,  # Convert to decimal
                'keyword_score': score_details.get('keyword_score', 0.0) / 100.0,
                'semantic_score': score_details.get('semantic_score', 0.0) / 100.0,
                'sector': sector_data.get('primary_sector', 'Unknown'),
                'is_relevant': result.get('relevance_label') in ['relevant', 'partially_relevant'],
                'keywords_found': result.get('found_keywords', []),
                'semantic_similarity': semantic_data.get('semantic_score', 0.0) / 100.0 if semantic_data else 0.0,
                'relevance_label': result.get('relevance_label', 'Unknown'),
                'analysis_notes': result.get('relevance_reason', ''),
                'content_summary': result.get('content_summary', '')[:200]
            })
    
    return processed_results, failed_sites


def _get_error_suggestion(error_message: str) -> str:
    """Generate helpful suggestion based on error type"""
    error_lower = error_message.lower()
    
    if 'cannot connect' in error_lower or 'connection' in error_lower:
        return "🌐 Sito non raggiungibile - Verifica che l'URL sia corretto e il sito sia online"
    elif 'timeout' in error_lower:
        return "⏱️ Timeout - Il sito è troppo lento o temporaneamente non disponibile"
    elif 'ssl' in error_lower or 'certificate' in error_lower:
        return "🔒 Errore certificato SSL - Verifica configurazione HTTPS del sito"
    elif '403' in error_lower or 'forbidden' in error_lower:
        return "🚫 Accesso negato - Il sito blocca l'accesso automatico (WAF/Firewall)"
    elif '404' in error_lower:
        return "❌ Pagina non trovata - Verifica che l'URL sia corretto"
    elif '503' in error_lower or 'service unavailable' in error_lower:
        return "⚠️ Servizio temporaneamente non disponibile - Riprova più tardi"
    elif 'redirect' in error_lower:
        return "🔄 Problema redirect - L'URL potrebbe essere cambiato"
    else:
        return "🔧 Errore tecnico - Contatta il supporto o verifica manualmente"



# Cache management endpoints
@router.post("/cache-analysis")
async def cache_analysis_results(analysis_id: str, results: List[Dict]):
    """Cache analysis results for later report generation"""
    analysis_cache[analysis_id] = results
    return {"message": f"Analysis results cached with ID: {analysis_id}"}


@router.get("/cached-analyses")
async def list_cached_analyses():
    """List all cached analysis results"""
    return {
        "cached_analyses": [
            {
                "analysis_id": aid,
                "competitor_count": len(results),
                "cached_at": datetime.now().isoformat()  # In production, store actual timestamp
            }
            for aid, results in analysis_cache.items()
        ]
    }