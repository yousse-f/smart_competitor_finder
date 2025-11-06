"""
🚫 Blacklist di domini difficili/impossibili da scrapare
Sistema intelligente per evitare timeout inutili
"""

# Domini IMPOSSIBILI da scrapare (blacklist)
IMPOSSIBLE_DOMAINS = {
    'mondo-convenienza.it': {
        'reason': 'Cloudflare Pro + IP blocking geografico',
        'last_tested': '2025-10-10',
        'error_type': 'timeout_all_methods',
        'recommendation': 'Skip - impossibile aggirare protezioni'
    },
    'ikea.com': {
        'reason': 'Anti-bot detection avanzato + Rate limiting',
        'last_tested': '2025-10-10', 
        'error_type': 'bot_detection',
        'recommendation': 'Skip - richiede proxy pool enterprise'
    }
}

# Domini DIFFICILI (timeout ridotto)
DIFFICULT_DOMAINS = {
    'natuzzi.com': {
        'reason': 'SSL certificate issues + slow response',
        'timeout_multiplier': 0.5,  # 50% del timeout normale
        'max_retries': 1
    }
}

# Domini FACILI (success garantito)
EASY_DOMAINS = {
    'calligaris.com': {
        'reason': 'Basic HTTP sempre funziona',
        'preferred_method': 'basic_http',
        'success_rate': 100
    },
    'boscoitalia.it': {
        'reason': 'Advanced scraper funziona bene',
        'preferred_method': 'advanced',
        'success_rate': 95
    }
}

def is_domain_impossible(url: str) -> bool:
    """Controlla se il dominio è nella blacklist"""
    domain = extract_domain(url)
    return domain in IMPOSSIBLE_DOMAINS

def get_domain_config(url: str) -> dict:
    """Ottieni configurazione specifica per dominio"""
    domain = extract_domain(url)
    
    if domain in IMPOSSIBLE_DOMAINS:
        return {'skip': True, 'reason': IMPOSSIBLE_DOMAINS[domain]['reason']}
    elif domain in DIFFICULT_DOMAINS:
        return {'difficult': True, **DIFFICULT_DOMAINS[domain]}
    elif domain in EASY_DOMAINS:
        return {'easy': True, **EASY_DOMAINS[domain]}
    else:
        return {'unknown': True}

def extract_domain(url: str) -> str:
    """Estrai dominio pulito da URL"""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.lower()
    # Rimuovi www. e porta
    domain = domain.replace('www.', '').split(':')[0]
    return domain

def should_skip_scraping(url: str) -> tuple[bool, str]:
    """
    Determina se saltare lo scraping di un URL
    Returns: (should_skip, reason)
    """
    config = get_domain_config(url)
    
    if config.get('skip'):
        return True, f"🚫 Blacklisted: {config['reason']}"
    
    return False, "OK to scrape"