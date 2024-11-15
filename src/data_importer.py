import osmium
import csv
import os
from typing import List, Dict, Union

# Define the structure of our data point
class DataPoint:
    def __init__(self, latitude: float, longitude: float, zip_code: Union[str, int]):
        self.latitude = latitude
        self.longitude = longitude
        self.zip_code = zip_code

    def as_vector(self):
        return [self.latitude, self.longitude]  # Expand with more dimensions as needed

# Factory for data ingestion
class DataIngestionFactory:
    @staticmethod
    def load_data(file_path: str) -> List[DataPoint]:
        if file_path.endswith('.csv'):
            return DataIngestionFactory._load_from_csv(file_path)
        elif file_path.endswith('.osm.pbf'):
            return DataIngestionFactory._load_from_pbf(file_path)
        else:
            raise ValueError("Unsupported file format")

    @staticmethod
    def _load_from_csv(file_path: str) -> List[DataPoint]:
        data = []
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(DataPoint(float(row['lat']), float(row['lng']), row['zip']))
        return data

    @staticmethod
    def _load_from_pbf(file_path: str) -> List[DataPoint]:
        class OSMHandler(osmium.SimpleHandler):
            def __init__(self):
                super().__init__()
                self.data = []

            def node(self, n):
                # Filter only nodes with necessary tags if available, here simplified
                if 'zip_code' in n.tags:
                    zip_code = n.tags.get('zip_code')
                    self.data.append(DataPoint(n.location.lat, n.location.lon, zip_code))

        handler = OSMHandler()
        handler.apply_file(file_path)
        return handler.data
    