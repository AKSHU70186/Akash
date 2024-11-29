import csv
import json
from typing import List, Dict, Any
from fastapi import HTTPException
import os

class DataExporter:
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data

    async def to_csv(self, filename: str) -> str:
        try:
            filepath = f"exports/{filename}.csv"
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if not self.data:
                    writer = csv.writer(f)
                    writer.writerow(['No data available'])
                else:
                    # Get headers from first item
                    headers = list(self.data[0].keys())
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(self.data)
            return filepath
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error exporting to CSV: {str(e)}")

    async def to_json(self, filename: str) -> str:
        try:
            filepath = f"exports/{filename}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return filepath
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error exporting to JSON: {str(e)}")

    async def to_txt(self, filename: str) -> str:
        try:
            filepath = f"exports/{filename}.txt"
            with open(filepath, 'w', encoding='utf-8') as f:
                for item in self.data:
                    f.write('---Article---\n')
                    for key, value in item.items():
                        f.write(f"{key}: {value}\n")
                    f.write('\n')
            return filepath
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error exporting to TXT: {str(e)}") 