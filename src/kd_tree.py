"""
Implementation of K-D Trees structure.
Slide 4 of the presentation offers a useful visual depiction:
https://docs.google.com/presentation/d/1cgaXUtRxTxCplw3CdPCHHPpMtw8CO0HeHZIf2TlUmZg/edit?usp=sharing
"""

import numpy as np
from data_importers import DataPoint, DataIngestionFactory
import heapq
import os
import itertools

from config import SAMPLE_DATA, OSM_DATA


class ApproximateKDTree:
    def __init__(self, data_points: list[DataPoint], max_depth: int = 10):
        self.max_depth = max_depth
        self.tree = self._build_tree(data_points)

    def _build_tree(self, points, depth=0):
        if not points:
            return None

        axis = depth % 2
        points.sort(key=lambda point: point.as_vector()[axis])
        median = len(points) // 2

        return {
            'point': points[median],
            'left': self._build_tree(points[:median], depth + 1),
            'right': self._build_tree(points[median + 1:], depth + 1)
        }

    def _distance(self, p1: DataPoint, p2: DataPoint):
        return np.linalg.norm(np.array(p1.as_vector()) - np.array(p2.as_vector()))

    def query(self, query_point, num_neighbors=5):
        """Query the KD-Tree using priority search for the k nearest neighbors."""
        heap = []                      # Max heap for k 'nearest neighbors'
        priority_queue = []            # Min heap for priority-based traversal...
        unique_id = itertools.count()  # Unique identifier for each node

        # Add root node to priority queue... (prioritized by proximity to query point)
        heapq.heappush(priority_queue, (0, next(unique_id), self.tree, 0))  # (priority, id, node, depth)

        while priority_queue:
            priority, _, node, depth = heapq.heappop(priority_queue)

            if node is None or depth > self.max_depth:
                continue

            # Calc dist to curr node
            dist = self._distance(query_point, node['point'])
            if len(heap) < num_neighbors:
                heapq.heappush(heap, (-dist, node['point']))
            elif dist < -heap[0][0]:
                heapq.heapreplace(heap, (-dist, node['point']))

            # Determine split axis (i.e. where rect split to form next smaller rect...)
            axis = depth % 2
            diff = query_point.as_vector()[axis] - node['point'].as_vector()[axis]

            # Add child nodes to priority queue
            nearer = node['left'] if diff < 0 else node['right']
            farther = node['right'] if diff < 0 else node['left']
            heapq.heappush(priority_queue, (0, next(unique_id), nearer, depth + 1))
            if abs(diff) < -heap[0][0] or len(heap) < num_neighbors:
                heapq.heappush(priority_queue, (abs(diff), next(unique_id), farther, depth + 1))

        # Extract results sorted by dist...
        return [item[1] for item in sorted(heap, key=lambda x: -x[0])]


if __name__ == '__main__':
    file_path = os.path.join(SAMPLE_DATA)
    data_points = DataIngestionFactory.load_data(file_path)

    approx_kd_tree = ApproximateKDTree(data_points, max_depth=10)

    # Test
    query_point = DataPoint(latitude=18.34, longitude=-64.92, zip_code=None)
    results = approx_kd_tree.query(query_point)

    print("Approximate KD Tree Nearest Neighbors:")
    for result in results:
        print(f"Zip Code: {result.zip_code}, Location: ({result.latitude}, {result.longitude})")
