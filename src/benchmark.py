import time
import numpy as np
from lsh import MultiTableLSH
from kd_tree import ApproximateKDTree
from data_importer import DataPoint, DataIngestionFactory
import os

from config import ROOT_DIR


def brute_force_search(data_points, query_point, k=5):
    return sorted(data_points, key=lambda p: np.linalg.norm(np.array(p.as_vector()) - np.array(query_point.as_vector())))[:k]

def benchmark(algorithm, data_points, num_queries=100, k=5):
    # Randomly select queries from data_points
    query_points = np.random.choice(data_points, num_queries, replace=False)
    
    # Benchmark accuracy and speed
    total_time = 0
    correct_retrievals = 0

    for query_point in query_points:
        # Ground-truth nearest neighbors (brute-force)
        ground_truth = set(p.zip_code for p in brute_force_search(data_points, query_point, k))

        # Measure query time
        start_time = time.time()
        results = algorithm.query(query_point, k)
        total_time += time.time() - start_time

        # Measure accuracy (intersection with ground truth)
        retrieved_zips = set(p.zip_code for p in results)
        correct_retrievals += len(retrieved_zips & ground_truth) / k

    avg_query_time = total_time / num_queries
    avg_accuracy = correct_retrievals / num_queries

    return avg_query_time, avg_accuracy

# Sample Usage
if __name__ == '__main__':
    file_path = os.path.join(ROOT_DIR, 'data', 'uszips.csv')
    data_points = DataIngestionFactory.load_data(file_path)
    
    # Multi-Table LSH
    lsh = MultiTableLSH(num_tables=3, hash_size=2)
    lsh.insert(data_points)
    
    # Approximate KD Tree
    approx_kd_tree = ApproximateKDTree(data_points, max_depth=10)

    # Benchmark Multi-Table LSH
    lsh_time, lsh_accuracy = benchmark(lsh, data_points)
    print(f"Multi-Table LSH - Time: {lsh_time:.5f}s, Accuracy: {lsh_accuracy:.2f}")

    # Benchmark Approximate KD Tree
    kd_time, kd_accuracy = benchmark(approx_kd_tree, data_points)
    print(f"Approximate KD Tree - Time: {kd_time:.5f}s, Accuracy: {kd_accuracy:.2f}")
