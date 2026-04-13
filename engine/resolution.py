from thefuzz import fuzz
from core import Target, DataPoint
from typing import List

class EntityResolver:
    """
    Validates findings to ensure they relate to the target and not a false positive.
    """
    def __init__(self, confidence_threshold: int = 50):
        self.confidence_threshold = confidence_threshold

    def resolve(self, target: Target, data_points: List[DataPoint]) -> List[DataPoint]:
        resolved_points = []
        
        # If no target specifics extracted, just return everything untouched but tagged 100
        if not target.name and not target.company:
            return data_points

        for dp in data_points:
            text_to_analyze = f"{dp.value} {dp.description}".lower()
            
            score_name = fuzz.partial_ratio(target.name.lower(), text_to_analyze) if target.name else 0
            score_company = fuzz.partial_ratio(target.company.lower(), text_to_analyze) if target.company else 0
            
            # Combine scores loosely
            if target.name and target.company:
                final_score = (score_name + score_company) // 2
            else:
                final_score = max(score_name, score_company)
                
            # Contextual validation for False Positives
            if target.location and target.location.lower() in text_to_analyze:
                final_score += 15
            if target.industry and target.industry.lower() in text_to_analyze:
                final_score += 15
                
            dp.confidence = min(100, final_score)
            
            # Filter based on threshold, or if it's infrastructure (which we guessed), keep it but maybe lower score
            if dp.category == "Technical Infrastructure":
                dp.confidence = min(100, dp.confidence + 40) # give domains a bump
            
            if dp.confidence >= self.confidence_threshold:
                resolved_points.append(dp)
                
        return resolved_points
