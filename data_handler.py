import pandas as pd
from datetime import datetime, timedelta
import json
import os
from typing import Optional


class DataHandler:
    def __init__(self, csv_path='data/readings.csv'):
        self.csv_path = csv_path
        self._ensure_csv_exists()

    def _ensure_csv_exists(self):
        """Create CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.csv_path):
            os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
            df = pd.DataFrame(columns=['timestamp', 'reading', 'latitude', 'longitude'])
            df.to_csv(self.csv_path, index=False)

    def save_reading(self, reading, metadata):
        """Save meter reading with metadata to CSV"""
        data = {
            'timestamp': metadata['timestamp'],
            'reading': reading,
            'latitude': metadata['latitude'],
            'longitude': metadata['longitude']
        }

        df = pd.DataFrame([data])
        df.to_csv(self.csv_path, mode='a', header=False, index=False)

    def calculate_consumption(self, period='daily', start: Optional[str] = None, end: Optional[str] = None):
        """Calculate consumption for specified period with optional ISO date range filtering"""
        if not os.path.exists(self.csv_path):
            return pd.DataFrame(columns=['first', 'last', 'consumption'])

        df = pd.read_csv(self.csv_path)
        if df.empty:
            return pd.DataFrame(columns=['first', 'last', 'consumption'])

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        # Apply date range filtering if provided (expects ISO 8601 or YYYY-MM-DD)
        if start:
            try:
                start_dt = pd.to_datetime(start)
                df = df[df['timestamp'] >= start_dt]
            except Exception:
                pass
        if end:
            try:
                end_dt = pd.to_datetime(end)
                df = df[df['timestamp'] <= end_dt]
            except Exception:
                pass

        if df.empty:
            return pd.DataFrame(columns=['first', 'last', 'consumption'])

        if period == 'daily':
            grouped = df.resample('D', on='timestamp')
        elif period == 'weekly':
            grouped = df.resample('W', on='timestamp')
        elif period == 'monthly':
            grouped = df.resample('M', on='timestamp')
        else:
            raise ValueError("Invalid period. Use 'daily', 'weekly', or 'monthly'")

        # Calculate consumption (difference between consecutive readings)
        consumption = grouped['reading'].agg(['first', 'last']).fillna(method='ffill')
        consumption['consumption'] = consumption['last'] - consumption['first']

        return consumption


