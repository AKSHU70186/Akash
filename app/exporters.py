import csv
import json
import pandas as pd
from typing import List, Dict, Any
import xlsxwriter
from fastapi import HTTPException
import boto3
from datetime import datetime

class DataExporter:
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data

    async def to_csv(self, filename: str) -> str:
        try:
            df = pd.DataFrame(self.data)
            filepath = f"exports/{filename}.csv"
            df.to_csv(filepath, index=False)
            return filepath
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error exporting to CSV: {str(e)}")

    async def to_json(self, filename: str) -> str:
        try:
            filepath = f"exports/{filename}.json"
            with open(filepath, 'w') as f:
                json.dump(self.data, f)
            return filepath
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error exporting to JSON: {str(e)}")

    async def to_excel(self, filename: str) -> str:
        try:
            df = pd.DataFrame(self.data)
            filepath = f"exports/{filename}.xlsx"
            with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
            return filepath
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error exporting to Excel: {str(e)}")

    async def upload_to_s3(self, filepath: str, bucket: str) -> str:
        try:
            s3 = boto3.client('s3')
            filename = filepath.split('/')[-1]
            s3.upload_file(filepath, bucket, filename)
            return f"https://{bucket}.s3.amazonaws.com/{filename}"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading to S3: {str(e)}") 