# Smart Competitor Finder - AI Coding Assistant Instructions

## Project Overview

**Smart Competitor Finder** is a web application that analyzes client websites to extract keywords and find relevant competitors from bulk Excel uploads. The system identifies pertinent competitors by matching keywords and scoring relevance.

### Architecture Stack
- **Frontend**: Next.js 14 + Tailwind CSS
- **Backend**: FastAPI (Python 3.11+) with REST API
- **Scraping Engine**: Playwright + BeautifulSoup + asyncio for JavaScript-enabled pages
- **Database**: PostgreSQL + SQLAlchemy for caching and logging
- **Reports**: Pandas + OpenPyXL for Excel generation
- **Future AI Layer**: OpenAI Embeddings/LangChain for semantic analysis

## Core Workflow

1. **Client Analysis**: Extract keywords from client website URL
2. **Keyword Selection**: User selects relevant service/product keywords  
3. **Bulk Processing**: Upload Excel with competitor URLs, process asynchronously
4. **Scoring**: Calculate match percentage based on keyword occurrences
5. **Report Generation**: Create Excel with match scores, found keywords, screenshots

## Key API Structure

```
/api/analyze-site   (POST) - Extract keywords from client URL
/api/upload-file    (POST) - Process competitor Excel file
/api/analyze-bulk   (POST) - Start bulk competitor analysis
/api/report         (GET)  - Download final Excel report
```

## Development Patterns

### Scraping Functions
- `extract_keywords(url)` - Main keyword extraction from client sites
- `search_keywords_in_sites(file, keywords)` - Bulk competitor analysis
- Use async/await for concurrent processing of multiple URLs

### Report Format
Excel output includes: URL, Match Score (%), Keywords Found, Screenshot availability
- Sort by match score descending
- Include keyword occurrence counts

### Performance Considerations
- Implement asynchronous scraping for bulk operations
- Cache analyzed sites in PostgreSQL to avoid re-scraping
- Use progress bars for long-running bulk operations

### Future Enhancements (Phase 2-3)  
- AI semantic filtering with embeddings and cosine similarity
- Interactive dashboard with clustering visualization
- Cloud scaling with Celery + Redis
- Multi-tenant authentication system
- CRM integration APIs

## File Organization

- Frontend components should handle keyword selection UI and progress tracking
- Backend should separate scraping logic from API endpoints
- Database models for caching site analysis results
- Report generation should be modular for different output formats

When implementing features, prioritize the MVP workflow described in `roadmap.md` and ensure asynchronous processing for scalability.