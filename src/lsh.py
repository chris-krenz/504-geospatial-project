"""
This is the Multi-Table LSH algo (discussed more in proposal)
"""

import numpy as np
from sklearn.random_projection import GaussianRandomProjection  # only skleran package I'm currently using...
from collections import defaultdict
from data_importers import DataPoint, DataIngestionFactory
import os

from config import SAMPLE_DATA


class MultiTableLSH:
    def __init__(self, num_tables: int, hash_size: int):
        self.num_tables = num_tables
        self.hash_size = hash_size
        self.hash_tables = [defaultdict(list) for _ in range(num_tables)]
        self.projections = [GaussianRandomProjection(n_components=hash_size) for _ in range(num_tables)]

    def _hash(self, vector, table_index):
        projected = self.projections[table_index].fit_transform([vector])[0]
        return tuple((projected > 0).astype(int))

    def insert(self, data_points: list[DataPoint]):
        for data_point in data_points:
            vector = data_point.as_vector()
            for i in range(self.num_tables):
                hash_key = self._hash(vector, i)
                self.hash_tables[i][hash_key].append(data_point)

    def query(self, query_point: DataPoint, num_neighbors: int = 10):
        candidate_set = set()
        query_vector = query_point.as_vector()

        for i in range(self.num_tables):
            hash_key = self._hash(query_vector, i)
            candidate_set.update(self.hash_tables[i].get(hash_key, []))

        neighbors = sorted(
            candidate_set,
            key=lambda point: np.linalg.norm(np.array(point.as_vector()) - np.array(query_vector))
        )

        return neighbors[:num_neighbors]


if __name__ == '__main__':

    file_path = os.path.join(SAMPLE_DATA)
    data_points = DataIngestionFactory.load_data(file_path)

    lsh = MultiTableLSH(num_tables=3, hash_size=2)
    lsh.insert(data_points)

    # test data
    query_point = DataPoint(latitude=18.34, longitude=-64.92, zip_code=None)
    # query_point = DataPoint(latitude=42.0, longitude=-71.0, zip_code=None, population=10_000, timezone='America/New_York')
    results = lsh.query(query_point)

    for result in results:
        print(f"Zip Code: {result.zip_code}, Location: ({result.latitude}, {result.longitude})")
