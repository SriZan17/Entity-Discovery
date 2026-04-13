from .base import BaseAdapter
from duckduckgo_search import DDGS
from core import DataPoint, Target
from typing import List

class ContextualAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(name="DuckDuckGo News", category="Contextual & Regulatory")

    def execute(self, target: Target) -> List[DataPoint]:
        self._apply_opsec_delay()
        results = []
        
        # Determine query
        query = target.company if target.company else target.raw_query
        
        try:
            with DDGS() as ddgs:
                news_results = ddgs.news(query, max_results=5)
                for r in news_results:
                    val = r.get("title", "News Mention")
                    desc = r.get("body", "")
                    url = r.get("url", "")
                    date = r.get("date", "")
                    
                    full_desc = f"Published on {date}. Snippet: {desc}"
                    
                    pt = DataPoint(
                        source_module=self.name,
                        category=self.category,
                        value=val,
                        description=full_desc,
                        url=url
                    )
                    results.append(pt)
        except Exception as e:
            print(f"[!] {self.name} encountered an error: {e}")
            
        return results
