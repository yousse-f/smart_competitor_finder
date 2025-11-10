from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from api.analyze_site import router as analyze_site_router
from api.upload_file import router as upload_file_router
from api.analyze_bulk import router as analyze_bulk_router
from api.upload_analyze import router as upload_analyze_router
from api.analyze_stream import router as analyze_stream_router
from api.report import router as report_router
from api.site_summary import router as site_summary_router
from api.list_analyses import router as list_analyses_router

# Initialize FastAPI app
app = FastAPI(
    title="Smart Competitor Finder API",
    description="API for analyzing websites and finding relevant competitors",
    version="1.0.0"
)

# CORS middleware for frontend integration
# Read allowed origins from environment variable
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(analyze_site_router, prefix="/api", tags=["analysis"])
app.include_router(upload_file_router, prefix="/api", tags=["file-processing"])
app.include_router(analyze_bulk_router, prefix="/api", tags=["bulk-analysis"])
app.include_router(upload_analyze_router, prefix="/api", tags=["upload-analysis"])
app.include_router(analyze_stream_router, prefix="/api", tags=["streaming-analysis"])
app.include_router(report_router, prefix="/api", tags=["reports"])
app.include_router(site_summary_router, prefix="/api", tags=["ai-analysis"])
app.include_router(list_analyses_router, tags=["analysis-management"])

@app.get("/")
async def root():
    return {"message": "Smart Competitor Finder API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    # Get port from environment variable (Railway uses $PORT)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("APP_ENV", "development") != "production"
    )