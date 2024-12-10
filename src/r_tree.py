from rtree import index  # R-Tree library
from data_importers import DataPoint, DataIngestionFactory
import os
import numpy as np


class RTree:
    def __init__(self):
        # Create R-Tree index with default properties
        self.idx = index.Index()

    def insert(self, data_points: list[DataPoint]):
        """Insert data points into the R-Tree."""
        for i, data_point in enumerate(data_points):
            # Insert each point as a bounding box (xmin, ymin, xmax, ymax)
            self.idx.insert(
                i,
                (data_point.longitude, data_point.latitude, data_point.longitude, data_point.latitude),
                obj=data_point,
            )

    # def query(self, query_point: DataPoint, num_neighbors=5):
    #     """Query the R-Tree for the k nearest neighbors."""
    #     # Perform a nearest neighbor search
    #     nearest = list(
    #         self.idx.nearest(
    #             (query_point.longitude, query_point.latitude, query_point.longitude, query_point.latitude),
    #             num_neighbors,
    #             objects=True,
    #         )
    #     )

    #     # Extract the DataPoint objects
    #     return [item.object for item in nearest]

    def query(self, query_point: DataPoint, num_neighbors=4, max_nodes=4):
        """Approximate query for k nearest neighbors with a limit on nodes explored."""
        visited_nodes = 0
        nearest_results = []

        # Custom generator to simulate early termination
        for nearest in self.idx.nearest(
            (query_point.longitude, query_point.latitude,
            query_point.longitude, query_point.latitude),
            num_neighbors * max_nodes,  # Oversample to ensure we get enough results
            objects=True,
        ):
            # Append results
            nearest_results.append(nearest.object)
            visited_nodes += 1

            # Stop once we've visited max_nodes
            if visited_nodes >= max_nodes:
                break

        # Return only the top-k results
        return nearest_results[:num_neighbors]


# Standalone execution
if __name__ == "__main__":
    # Load sample data
    file_path = os.path.join("data", "uszips.csv")  # Update path as needed
    data_points = DataIngestionFactory.load_data(file_path)

    # Initialize the R-Tree
    rtree_ann = RTree()
    rtree_ann.insert(data_points)

    # Perform a sample query
    query_point = DataPoint(latitude=18.34, longitude=-64.92, zip_code=None)  # Example query
    results = rtree_ann.query(query_point, num_neighbors=5)

    # Print results
    print("R-Tree Nearest Neighbors:")
    for result in results:
        print(f"Zip Code: {result.zip_code}, Location: ({result.latitude}, {result.longitude})")
        