import numpy as np
from sklearn.random_projection import GaussianRandomProjection
from collections import defaultdict
from data_importer import DataPoint, DataIngestionFactory
import random
import os

from config import ROOT_DIR


class MultiTableLSH:
    def __init__(self, num_tables: int, hash_size: int):
        self.num_tables = num_tables
        self.hash_size = hash_size
        self.hash_tables = [defaultdict(list) for _ in range(num_tables)]
        self.projections = [GaussianRandomProjection(n_components=hash_size) for _ in range(num_tables)]

    def _hash(self, vector, table_index):
        projected = self.projections[table_index].fit_transform([vector])[0]
        return tuple((projected > 0).astype(int))  # Simple binary hash

    def insert(self, data_points: list[DataPoint]):
        for data_point in data_points:
            vector = data_point.as_vector()
            for i in range(self.num_tables):
                hash_key = self._hash(vector, i)
                self.hash_tables[i][hash_key].append(data_point)

    def query(self, query_point: DataPoint, num_neighbors: int = 5):
        candidate_set = set()
        query_vector = query_point.as_vector()

        # Gather candidates from each hash table
        for i in range(self.num_tables):
            hash_key = self._hash(query_vector, i)
            candidate_set.update(self.hash_tables[i].get(hash_key, []))

        # Compute actual distances to the query point
        neighbors = sorted(
            candidate_set,
            key=lambda point: np.linalg.norm(np.array(point.as_vector()) - np.array(query_vector))
        )

        return neighbors[:num_neighbors]

# Sample usage
if __name__ == '__main__':
    # Load the data from a CSV or PBF file
    file_path = os.path.join(ROOT_DIR, 'data', 'simplemaps_uszips_basicv1.86', 'uszips.csv')  # Update path as needed
    data_points = DataIngestionFactory.load_data(file_path)

    # Initialize Multi-Table LSH with desired parameters
    lsh = MultiTableLSH(num_tables=3, hash_size=2)  # Adjust hash_size as dimensionality grows
    lsh.insert(data_points)

    # Perform a query
    query_point = DataPoint(latitude=18.34, longitude=-64.92, zip_code=None)  # Example query
    results = lsh.query(query_point)

    # Print nearest neighbors
    for result in results:
        print(f"Zip Code: {result.zip_code}, Location: ({result.latitude}, {result.longitude})")
