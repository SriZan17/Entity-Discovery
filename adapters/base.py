import random
import time
from urllib import robotparser
from urllib.parse import urlparse
from abc import ABC, abstractmethod
from typing import List, Optional
from core import DataPoint, Target

POPULAR_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
]

class BaseAdapter(ABC):
    """
    Base adapter class enforcing modularity and OPSEC (jitter, headers).
    """
    def __init__(self, name: str, category: str, proxies: Optional[List[str]] = None):
        self.name = name
        self.category = category
        # Basic proxy rotation support
        self.proxies = proxies if proxies else []
        self._rp_cache = {}

    def _get_proxy(self) -> Optional[dict]:
        """Rotates through available proxies."""
        if not self.proxies:
            return None
        proxy_url = random.choice(self.proxies)
        return {"http": proxy_url, "https": proxy_url}

    def _can_fetch(self, url: str) -> bool:
        """Respects robots.txt rules for the given URL."""
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = f"{base_url}/robots.txt"
        
        if base_url not in self._rp_cache:
            rp = robotparser.RobotFileParser()
            try:
                rp.set_url(robots_url)
                rp.read()
                self._rp_cache[base_url] = rp
            except Exception:
                # If robots.txt fails to load, fail open (or closed based on strictness)
                self._rp_cache[base_url] = None
                
        rp = self._rp_cache.get(base_url)
        if rp:
            return rp.can_fetch(self._get_random_user_agent(), url)
        return True

    def _get_random_user_agent(self) -> str:
        return random.choice(POPULAR_USER_AGENTS)

    def _apply_opsec_delay(self, min_wait: float = 1.0, max_wait: float = 3.0):
        """Implement a jitter delay to mimic human browsing and avoid rate-limiting."""
        time.sleep(random.uniform(min_wait, max_wait))

    @abstractmethod
    def execute(self, target: Target) -> List[DataPoint]:
        """
        Executes the acquisition logic for this adapter.
        Must return a list of DataPoint objects.
        """
        pass
