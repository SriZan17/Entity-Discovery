from .base import BaseAdapter
from duckduckgo_search import DDGS
from core import DataPoint, Target
from typing import List

class SearchAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(name="DuckDuckGo Search", category="Social & Public Footprint")

    def execute(self, target: Target) -> List[DataPoint]:
        # Emulate OPSEC delay
        self._apply_opsec_delay()
        
        results = []
        # Construct Dork-like queries
        # e.g., "Travis Haasch" "AIGeeks" site:linkedin.com
        queries = []
        if target.name and target.company:
            queries.append(f'"{target.name}" "{target.company}" site:linkedin.com')
            queries.append(f'"{target.name}" "{target.company}"')
        else:
            queries.append(target.raw_query)

        try:
            with DDGS() as ddgs:
                for query in queries:
                    # search DDG
                    search_results = ddgs.text(query, max_results=5)
                    for r in search_results:
                        desc = r.get("body", "")
                        url = r.get("href", "")
                        
                        pt = DataPoint(
                            source_module=self.name,
                            category=self.category,
                            value=r.get("title", "Search Result"),
                            description=desc,
                            url=url
                        )
                        results.append(pt)
        except Exception as e:
            # Handle potential rate-limits or network errors gracefully
            print(f"[!] {self.name} encountered an error: {e}")
            
        return results
