from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
import re

class DataTransformationPipeline:
    def __init__(self, steps: List[Dict[str, Any]]):
        self.steps = steps

    async def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        transformed_data = data.copy()
        for step in self.steps:
            transformer = self.get_transformer(step['type'])
            transformed_data = await transformer(transformed_data, step['config'])
        return transformed_data

    def get_transformer(self, transformer_type: str):
        transformers = {
            'clean_text': self.clean_text,
            'normalize_dates': self.normalize_dates,
            'extract_numbers': self.extract_numbers,
            'categorize': self.categorize
        }
        return transformers.get(transformer_type)

    async def clean_text(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        for field in config['fields']:
            if field in data:
                # Remove HTML tags
                data[field] = re.sub(r'<[^>]+>', '', str(data[field]))
                # Remove extra whitespace
                data[field] = ' '.join(data[field].split())
        return data

    async def normalize_dates(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        for field in config['fields']:
            if field in data:
                try:
                    date = pd.to_datetime(data[field])
                    data[field] = date.isoformat()
                except:
                    pass
        return data

    async def extract_numbers(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        for field in config['fields']:
            if field in data:
                numbers = re.findall(r'\d+\.?\d*', str(data[field]))
                data[f"{field}_numbers"] = [float(n) for n in numbers]
        return data

    async def categorize(self, data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        for field, categories in config['categories'].items():
            if field in data:
                for category, keywords in categories.items():
                    if any(keyword.lower() in str(data[field]).lower() for keyword in keywords):
                        data[f"{field}_category"] = category
                        break
        return data 