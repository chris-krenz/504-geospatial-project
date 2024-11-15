"""
This is the KD-Trees algo (discussed more in proposal)
"""

import numpy as np
from data_importer import DataPoint, DataIngestionFactory
import heapq
import os

from CONFIG import SAMPLE_DATA


class ApproximateKDTree:
    # TODO: priority search...

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

    def _search(self, node, query_point, depth, k, heap):
        if node is None or depth > self.max_depth:
            return

        dist = self._distance(query_point, node['point'])
        if len(heap) < k:
            heapq.heappush(heap, (-dist, node['point']))
        elif dist < -heap[0][0]:
            heapq.heapreplace(heap, (-dist, node['point']))

        axis = depth % 2
        diff = query_point.as_vector()[axis] - node['point'].as_vector()[axis]

        if diff < 0:
            self._search(node['left'], query_point, depth + 1, k, heap)
            if abs(diff) < -heap[0][0]:
                self._search(node['right'], query_point, depth + 1, k, heap)
        else:
            self._search(node['right'], query_point, depth + 1, k, heap)
            if abs(diff) < -heap[0][0]:
                self._search(node['left'], query_point, depth + 1, k, heap)

    def query(self, query_point: DataPoint, k=5):
        heap = []
        self._search(self.tree, query_point, 0, k, heap)
        return [item[1] for item in sorted(heap, reverse=True)]


if __name__ == '__main__':

    file_path = os.path.join(SAMPLE_DATA)
    data_points = DataIngestionFactory.load_data(file_path)

    approx_kd_tree = ApproximateKDTree(data_points, max_depth=10)

    # test
    query_point = DataPoint(latitude=18.34, longitude=-64.92, zip_code=None)
    results = approx_kd_tree.query(query_point)

    print("Approximate KD Tree Nearest Neighbors:")
    for result in results:
        print(f"Zip Code: {result.zip_code}, Location: ({result.latitude}, {result.longitude})")
