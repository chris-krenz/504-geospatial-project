from data_importers import DataPoint, DataIngestionFactory
import os


class RTreeNode:
    """Represents a node in the R-Tree."""
    def __init__(self, is_leaf=True):
        self.is_leaf = is_leaf
        self.children = []  # Child nodes or data points
        self.mbr = None     # Minimum Bounding Rectangle [xmin, ymin, xmax, ymax]

    def compute_mbr(self):
        """Compute the Minimum Bounding Rectangle (MBR) for the node."""
        if not self.children:
            return None

        # Combine MBRs of all children
        xmins, ymins, xmaxs, ymaxs = zip(*(child['mbr'] for child in self.children))
        self.mbr = [min(xmins), min(ymins), max(xmaxs), max(ymaxs)]


class RTree:
    """Simple R-Tree implementation."""
    def __init__(self, max_children=4):
        self.root = RTreeNode()
        self.max_children = max_children

    def insert(self, point, mbr):
        """Insert a DataPoint into the R-Tree."""
        leaf = self._choose_leaf(self.root, mbr)
        leaf.children.append({'point': point, 'mbr': mbr})
        leaf.compute_mbr()

        if len(leaf.children) > self.max_children:
            self._split_node(leaf)

    def _choose_leaf(self, node, mbr):
        """Choose the best leaf node to insert into."""
        if node.is_leaf:
            return node

        # Choose the child node with the least enlargement
        best_child = min(node.children, key=lambda child: self._enlargement(child['mbr'], mbr))
        return self._choose_leaf(best_child['node'], mbr)  # Access the child node via 'node' key

    def _enlargement(self, parent_mbr, new_mbr):
        """Calculate how much the parent MBR would need to grow to include new MBR."""
        xmin = min(parent_mbr[0], new_mbr[0])
        ymin = min(parent_mbr[1], new_mbr[1])
        xmax = max(parent_mbr[2], new_mbr[2])
        ymax = max(parent_mbr[3], new_mbr[3])
        new_area = (xmax - xmin) * (ymax - ymin)
        current_area = (parent_mbr[2] - parent_mbr[0]) * (parent_mbr[3] - parent_mbr[1])
        return new_area - current_area

    def _split_node(self, node):
        """Split a node into two nodes."""
        # Ensure we're splitting correctly based on leaf status
        is_leaf = node.is_leaf

        # Sort children and divide them into two groups
        node.children.sort(key=lambda child: child['mbr'][0])  # Sort by xmin
        mid = len(node.children) // 2
        left_children, right_children = node.children[:mid], node.children[mid:]

        # Create new nodes for the split
        left_node = RTreeNode(is_leaf=is_leaf)
        right_node = RTreeNode(is_leaf=is_leaf)
        left_node.children = left_children
        right_node.children = right_children

        # Recompute MBRs for the new nodes
        left_node.compute_mbr()
        right_node.compute_mbr()

        # Update the parent node
        node.is_leaf = False
        node.children = [
            {'node': left_node, 'mbr': left_node.mbr},
            {'node': right_node, 'mbr': right_node.mbr},
        ]

        # Update the parent's MBR
        node.compute_mbr()

    def query(self, query_point, k=1):
        """Query for the k nearest neighbors."""
        candidates = []
        self._nearest_neighbors(self.root, query_point, k, candidates)
        return [candidate['point'] for candidate in sorted(candidates, key=lambda c: c['distance'])[:k]]

    def _nearest_neighbors(self, node, query_point, k, candidates):
        """Recursive nearest neighbor search."""
        if node.is_leaf:
            for child in node.children:
                distance = self._distance(query_point, child['mbr'])
                candidates.append({'point': child['point'], 'distance': distance})
            return

        for child in sorted(node.children, key=lambda child: self._distance(query_point, child['mbr'])):
            if len(candidates) < k or self._distance(query_point, child['mbr']) < max(c['distance'] for c in candidates):
                self._nearest_neighbors(child['node'], query_point, k, candidates)

    def _distance(self, query_point, mbr):
        """Calculate the minimum distance from a query point to an MBR."""
        # Extract coordinates if query_point is a DataPoint
        if isinstance(query_point, DataPoint):
            x, y = query_point.longitude, query_point.latitude
        else:
            x, y = query_point  # If it's already a tuple/list

        xmin, ymin, xmax, ymax = mbr
        dx = max(xmin - x, 0, x - xmax)
        dy = max(ymin - y, 0, y - ymax)
        return dx**2 + dy**2  # Squared Euclidean distance


if __name__ == "__main__":
    # Load the uszips.csv file
    file_path = os.path.join("data", "uszips.csv")
    data_points = DataIngestionFactory.load_data(file_path)

    # Create and populate the R-Tree
    rtree = RTree(max_children=4)
    for point in data_points:
        mbr = [point.longitude, point.latitude, point.longitude, point.latitude]
        rtree.insert(point, mbr)

    # Perform a sample query
    query_point = [-64.92, 18.34]  # Longitude, Latitude (ensure order matches)
    results = rtree.query(query_point, k=5)

    print("Nearest Neighbors:")
    for result in results:
        print(f"Zip Code: {result.zip_code}, Location: ({result.latitude}, {result.longitude})")
