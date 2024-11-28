from pydantic import BaseModel, validator, HttpUrl
from typing import Dict, List, Optional
from datetime import datetime

class ScrapedDataValidator(BaseModel):
    source_url: HttpUrl
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]]

    @validator('data')
    def validate_data_structure(cls, v):
        required_fields = ['title', 'content']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Missing required field: {field}")
        return v

    @validator('metadata')
    def validate_metadata(cls, v):
        if v and 'scraper_version' not in v:
            raise ValueError("Metadata must include scraper_version")
        return v

class DataQualityChecker:
    def __init__(self, rules: Dict[str, Any]):
        self.rules = rules

    async def check_quality(self, data: Dict[str, Any]) -> Dict[str, bool]:
        results = {}
        for field, rule in self.rules.items():
            if field in data:
                results[field] = self.apply_rule(data[field], rule)
        return results

    def apply_rule(self, value: Any, rule: Dict[str, Any]) -> bool:
        if rule['type'] == 'length':
            return len(str(value)) >= rule['min_length']
        elif rule['type'] == 'range':
            return rule['min'] <= float(value) <= rule['max']
        elif rule['type'] == 'regex':
            import re
            return bool(re.match(rule['pattern'], str(value)))
        return True 