"""
Imports data from either .pbf files (from OSM) or .csv

https://mygeodata.cloud/converter/pbf-to-csv

NOTE: I experimented with including timezone and population data, but it was too sparse to be useful...
"""

import osmium  # used for parsing OSM (Open Street Map) files
import csv
import os
from typing import List, Dict, Union


class DataPoint:
    def __init__(self, latitude: float, longitude: float, zip_code: Union[str, int], 
                #  timezone: str='', population: int=0
                 ):
        self.latitude   = latitude
        self.longitude  = longitude
        self.zip_code   = zip_code
        # self.timezone   = timezone
        # self.population = population

    def as_vector(self):
        return [self.longitude, self.latitude]  # shoudl be able to add more dims here later

#... tryin to accommodate various data source types...
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
                data.append(DataPoint(
                        latitude=float(row['lat']), 
                        longitude=float(row['lng']), 
                        zip_code=row['zip'],
                        # timezone=row['timezone'] if row['timezone'] else 'Unknown',
                        # population=int(row['population']) if row['population'].isdigit() else 0
                    ))
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
    