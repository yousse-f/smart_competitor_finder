"""
Centralized configuration for Smart Competitor Finder backend.

This module provides a single source of truth for all configurable parameters,
making it easier to tune the system for different environments (local, Railway, production).
"""

import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class ScrapingConfig:
    """Scraping and browser automation configuration"""
    
    # === Timeouts (seconds) ===
    BROWSER_POOL_TIMEOUT: int = int(os.getenv("BROWSER_POOL_TIMEOUT", "15"))
    ADVANCED_SCRAPER_TIMEOUT: int = int(os.getenv("ADVANCED_SCRAPER_TIMEOUT", "20"))
    BASIC_HTTP_TIMEOUT: int = int(os.getenv("BASIC_HTTP_TIMEOUT", "5"))
    BULK_ANALYSIS_TIMEOUT: int = int(os.getenv("BULK_ANALYSIS_TIMEOUT", "600"))  # 10 minutes
    
    # === Concurrency Limits ===
    MAX_CONCURRENT_SCRAPES: int = int(os.getenv("MAX_CONCURRENT_SCRAPES", "2"))
    BROWSER_POOL_SIZE: int = int(os.getenv("BROWSER_POOL_SIZE", "1"))  # Reduced for Railway
    MAX_REQUESTS_PER_SESSION: int = int(os.getenv("MAX_REQUESTS_PER_SESSION", "20"))
    
    # === Scraping Mode ===
    SCRAPING_MODE: str = os.getenv("SCRAPING_MODE", "development")  # development, production
    
    # === External Services ===
    SCRAPINGBEE_API_KEY: Optional[str] = os.getenv("SCRAPINGBEE_API_KEY")
    SCRAPERAPI_API_KEY: Optional[str] = os.getenv("SCRAPERAPI_API_KEY")
    SCRAPERAPI_ENABLED: bool = os.getenv("SCRAPERAPI_ENABLED", "false").lower() == "true"

@dataclass
class AIConfig:
    """AI and ML configuration"""
    
    # === OpenAI ===
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MAX_RETRIES: int = int(os.getenv("OPENAI_MAX_RETRIES", "3"))
    OPENAI_TIMEOUT: int = int(os.getenv("OPENAI_TIMEOUT", "30"))
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    
    # === Semantic Analysis ===
    SEMANTIC_ANALYSIS_ENABLED: bool = os.getenv("SEMANTIC_ANALYSIS_ENABLED", "true").lower() == "true"
    SEMANTIC_THRESHOLD: float = float(os.getenv("SEMANTIC_THRESHOLD", "0.7"))
    KEYWORD_WEIGHT: float = float(os.getenv("KEYWORD_WEIGHT", "0.4"))
    SEMANTIC_WEIGHT: float = float(os.getenv("SEMANTIC_WEIGHT", "0.6"))

@dataclass
class ServerConfig:
    """Server and API configuration"""
    
    # === API ===
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    MAX_CONCURRENT_REQUESTS: int = int(os.getenv("MAX_CONCURRENT_REQUESTS", "2"))
    
    # === Storage ===
    REPORTS_DIR: str = os.getenv("REPORTS_DIR", "reports")

# Global config instances
scraping_config = ScrapingConfig()
ai_config = AIConfig()
server_config = ServerConfig()

# Validation
def validate_config():
    """Validate critical configuration"""
    errors = []
    
    if not ai_config.OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is not set")
    
    if scraping_config.MAX_CONCURRENT_SCRAPES < 1:
        errors.append("MAX_CONCURRENT_SCRAPES must be >= 1")
    
    if scraping_config.BROWSER_POOL_SIZE < 1:
        errors.append("BROWSER_POOL_SIZE must be >= 1")
    
    if ai_config.KEYWORD_WEIGHT + ai_config.SEMANTIC_WEIGHT != 1.0:
        errors.append(f"KEYWORD_WEIGHT ({ai_config.KEYWORD_WEIGHT}) + SEMANTIC_WEIGHT ({ai_config.SEMANTIC_WEIGHT}) must equal 1.0")
    
    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

# Run validation on import
validate_config()
