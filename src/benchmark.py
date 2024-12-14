"""
This is one of the main scripts that runs all algos and compares tehir accuracy and run times.
This is also the script that is run via Docker.
"""

import os
import time
import numpy as np
from lsh import MultiTableLSH
from kd_tree import ApproximateKDTree
from r_tree import RTree

from data_importers import DataIngestionFactory
import logging as log

from config import SAMPLE_DATA


def brute_force_search(data_points, query_point, k=5):
    """Brute search against which other algos are benchmarked, i.e. the 'ground truth'..."""
    return sorted(data_points, key=lambda p: np.linalg.norm(np.array(p.as_vector()) - np.array(query_point.as_vector())))[:k]

def benchmark(algorithm, data_points, num_queries=100, k=5):
    """Assess speed and accuracy..."""
    query_points = np.random.choice(data_points, num_queries, replace=False)
    
    total_time = 0
    correct_retrievals = 0  # Relative to brute force ground truth.

    for query_point in query_points:
        # brute foce...
        ground_truth = set(p.zip_code for p in brute_force_search(data_points, query_point, k))

        # Measure time
        start_time = time.time()
        results = algorithm.query(query_point, k)
        total_time += time.time() - start_time

        # Measure acc
        retrieved_zips = set(p.zip_code for p in results)
        correct_retrievals += len(retrieved_zips & ground_truth) / k

    avg_query_time = total_time / num_queries
    avg_accuracy = correct_retrievals / num_queries

    return avg_query_time, avg_accuracy


def sample_data_benchmark():
    """Benchmark LSH, KD-Tree, and R-Tree algos..."""
    file_path = os.path.join(SAMPLE_DATA)
    data_points = DataIngestionFactory.load_data(file_path)
    
    # K-D Tree
    approx_kd_tree = ApproximateKDTree(data_points, max_depth=10)
    kd_time, kd_accuracy = benchmark(approx_kd_tree, data_points)
    log.info(f"Approximate KD Tree - Time: {kd_time:.5f}s, Accuracy: {kd_accuracy:.2f}")

    # LSH #
    lsh = MultiTableLSH(num_tables=3, hash_size=2)
    lsh.insert(data_points)
    lsh_time, lsh_accuracy = benchmark(lsh, data_points)
    log.info(f"Multi-Table LSH - Time: {lsh_time:.5f}s, Accuracy: {lsh_accuracy:.2f}")

    # R-Tree #
    # max_children is the max num of children the node can hold before needing to split...
    # adjusting this allows you to choose a trade off between speed and accuracy
    # values around 128 will approach 100% accuracy but will be slighly slower
    # min value is 2, which yields an accuracy of about 43%.
    r_tree = RTree(max_children=64)  
    r_tree.insert(data_points)

    rtree_time, rtree_accuracy = benchmark(r_tree, data_points)
    log.info(f"R-Tree - Time: {rtree_time:.5f}s, Accuracy: {rtree_accuracy:.2f}")


if __name__ == "__main__":
    log.basicConfig(level=log.INFO)
    sample_data_benchmark()
    