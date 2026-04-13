from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Target:
    raw_query: str
    name: str = ""
    company: str = ""
    title: str = ""
    location: str = ""
    industry: str = ""


@dataclass
class DataPoint:
    source_module: str
    category: str # "social", "infrastructure", "contextual", etc.
    value: str
    description: str
    url: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    confidence: int = 100 # 0-100 scale 
    risk_level: str = "Low" # "Low", "Medium", "High", "Critical"

@dataclass
class IntelligenceReport:
    target: Target
    data_points: List[DataPoint] = field(default_factory=list)
    executive_summary: str = ""
    
    def get_by_category(self, category: str) -> List[DataPoint]:
        return [dp for dp in self.data_points if dp.category == category]
