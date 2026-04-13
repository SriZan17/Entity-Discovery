from core import DataPoint
from typing import List

class RiskEngine:
    """
    Evaluates resolved data points and assigns risk scores.
    """
    def __init__(self):
        # Basic keyword rules for prototype
        self.critical_keywords = ["breach", "leak", "pwned", "password", "exposed", "vulnerability"]
        self.high_keywords = ["expired ssl", "open port", "fraud", "lawsuit"]
        self.medium_keywords = ["controversy", "scandal", "unregistered", "warning"]

    def evaluate(self, data_points: List[DataPoint]):
        for dp in data_points:
            text = f"{dp.value} {dp.description}".lower()
            
            risk = "Low"
            
            # Check Critical
            if any(k in text for k in self.critical_keywords):
                risk = "Critical"
            elif any(k in text for k in self.high_keywords):
                risk = "High"
            elif any(k in text for k in self.medium_keywords):
                risk = "Medium"
                
            dp.risk_level = risk
