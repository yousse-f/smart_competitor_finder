"""
🎯 User-Agent Rotation Pool - Professional Anti-Detection
Sistema di rotazione intelligente per eludere WAF e anti-bot detection
"""

import random
from typing import List

class UserAgentRotator:
    """Professional User-Agent rotation for advanced anti-detection"""
    
    def __init__(self):
        # Pool di 15+ User-Agent professionali e recenti
        self.user_agents = [
            # Chrome 120+ (Latest)
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            
            # Chrome 119
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Firefox Latest
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
            
            # Safari Latest
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            
            # Edge Latest  
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.121',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.2210.121',
            
            # Chrome Mobile (Important for evasion)
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/120.0.6099.119 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0',
            'Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        ]
    
    def get_random_ua(self) -> str:
        """Get a random User-Agent from the pool"""
        return random.choice(self.user_agents)
    
    def get_complete_headers(self) -> dict:
        """Get complete professional headers with random UA"""
        ua = self.get_random_ua()
        
        # Determine browser type for consistent headers
        is_chrome = 'Chrome' in ua and 'Edg' not in ua
        is_firefox = 'Firefox' in ua
        is_safari = 'Safari' in ua and 'Chrome' not in ua
        is_mobile = 'Mobile' in ua or 'iPhone' in ua or 'Android' in ua
        
        headers = {
            'User-Agent': ua,
            'Accept-Language': random.choice([
                'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
                'it-IT,it;q=0.8,en-US;q=0.5,en;q=0.3',
                'it,en-US;q=0.7,en;q=0.3'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        if is_chrome:
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?1' if is_mobile else '?0',
                'sec-ch-ua-platform': '"Android"' if 'Android' in ua else '"macOS"' if 'Mac' in ua else '"Windows"'
            })
        elif is_firefox:
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Sec-GPC': '1' if random.random() > 0.5 else None
            })
        elif is_safari:
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            })
            
        # Remove None values
        return {k: v for k, v in headers.items() if v is not None}

# Global instance
ua_rotator = UserAgentRotator()