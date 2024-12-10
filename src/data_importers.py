"""
Imports data from either .pbf files (from OSM) or .csv

https://mygeodata.cloud/converter/pbf-to-csv

TODO: Expand to other data types...
"""

import osmium  # used for parsing OSM (Open Street Map) files
import csv
import os
from typing import List, Dict, Union


class DataPoint:
    def __init__(self, latitude: float, longitude: float, zip_code: Union[str, int]):
        self.latitude = latitude
        self.longitude = longitude
        self.zip_code = zip_code

    def as_vector(self):
        return [self.latitude, self.longitude]  # shoudl be able to add more dims here later


class DataIngestionFactory:  # trying to accommodate different data sources to increase potential dims
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
                if 'zip_code' in n.tags:
                    zip_code = n.tags.get('zip_code')
                    self.data.append(DataPoint(n.location.lat, n.location.lon, zip_code))

        handler = OSMHandler()
        handler.apply_file(file_path)
        return handler.data
    