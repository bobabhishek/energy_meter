import os
import pandas as pd
from typing import Optional

class DataHandler:
    def __init__(self, csv_path='data/readings.csv'):
        self.csv_path = csv_path
        self._ensure_csv_exists()

    def _ensure_csv_exists(self):
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w') as f:
                f.write('timestamp,reading,latitude,longitude\n')

    def save_reading(self, reading, metadata):
        data = {
            'timestamp': metadata['timestamp'],
            'reading': reading,
            'latitude': metadata['latitude'],
            'longitude': metadata['longitude']
        }
        df = pd.DataFrame([data])
        df.to_csv(self.csv_path, mode='a', header=False, index=False)

    def calculate_consumption(self, period='daily', start: Optional[str] = None, end: Optional[str] = None):
        if not os.path.exists(self.csv_path):
            return []

        df = pd.read_csv(self.csv_path)
        if df.empty:
            print('DEBUG: DataFrame is empty after filtering')
            return []

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')

        # Only filter if start/end are provided and not empty
        if start:
            try:
                if start.strip():
                    start_dt = pd.to_datetime(start)
                    df = df[df['timestamp'] >= start_dt]
            except Exception:
                pass
        if end:
            try:
                if end.strip():
                    end_dt = pd.to_datetime(end)
                    df = df[df['timestamp'] <= end_dt]
            except Exception:
                pass

        if df.empty:
            print('DEBUG: DataFrame is empty after filtering')
            return []

        if period == 'daily':
            grouped = df.resample('D', on='timestamp')
        elif period == 'weekly':
            grouped = df.resample('W', on='timestamp')
        elif period == 'monthly':
            grouped = df.resample('M', on='timestamp')
        else:
            raise ValueError("Invalid period. Use 'daily', 'weekly', or 'monthly'")

        # Calculate consumption (difference between consecutive readings)
        summary = grouped['reading'].agg(['first', 'last', 'count'])
        summary['consumption'] = summary['last'] - summary['first']
        # Only keep periods with at least two readings
        summary = summary[summary['count'] >= 2]
        print('DEBUG: Summary after grouping and filtering:')
        print(summary)
        summary = summary.reset_index()
        summary['timestamp'] = summary['timestamp'].astype(str)
        # Remove the 'count' column from output
        summary = summary.drop(columns=['count'])
        print('DEBUG: Final summary to return:')
        print(summary)
        return summary.to_dict(orient='records')
