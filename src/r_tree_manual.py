from data_importers import DataPoint, DataIngestionFactory
import os


class RTreeNode:
    def __init__(self, is_leaf=True, parent=None):
        self.is_leaf = is_leaf
        self.children = []
        self.mbr = None
        self.parent = parent

    def compute_mbr(self):
        if not self.children:
            self.mbr = None
            return
        xmins, ymins, xmaxs, ymaxs = zip(*(child['mbr'] for child in self.children))
        self.mbr = [min(xmins), min(ymins), max(xmaxs), max(ymaxs)]



class RTree:
    def __init__(self, max_children=32):
        self.root = RTreeNode()
        self.max_children = max_children

    def insert(self, points):
        for point in points:
            mbr = [point.longitude, point.latitude, point.longitude, point.latitude]
            leaf = self._choose_leaf(self.root, mbr)
            leaf.children.append({'point': point, 'mbr': mbr})
            # Leaf children are data points, no parent needed since these aren't nodes.
            leaf.compute_mbr()
            self._handle_overflow(leaf)

    def _handle_overflow(self, node):
        while len(node.children) > self.max_children:
            left_node, right_node = self._split_node(node)

            if node == self.root:
                # Create new root
                new_root = RTreeNode(is_leaf=False, parent=None)
                self.root = new_root
                left_node.parent = new_root
                right_node.parent = new_root
                new_root.children = [
                    {'node': left_node, 'mbr': left_node.mbr},
                    {'node': right_node, 'mbr': right_node.mbr}
                ]
                new_root.compute_mbr()
                return
            else:
                parent = node.parent
                # Remove old reference to node from parent
                for i, ch in enumerate(parent.children):
                    if ('node' in ch and ch['node'] == node):
                        parent.children.pop(i)
                        break

                left_node.parent = parent
                right_node.parent = parent

                parent.children.append({'node': left_node, 'mbr': left_node.mbr})
                parent.children.append({'node': right_node, 'mbr': right_node.mbr})
                parent.compute_mbr()
                node = parent

    def _split_node(self, node):
        children = node.children
        is_leaf = node.is_leaf

        seed1, seed2 = self._pick_seeds(children)
        left_children = [children[seed1]]
        right_children = [children[seed2]]

        remaining = [c for i, c in enumerate(children) if i not in (seed1, seed2)]

        for c in remaining:
            left_expansion = self._expansion(left_children, c)
            right_expansion = self._expansion(right_children, c)
            if left_expansion < right_expansion:
                left_children.append(c)
            else:
                right_children.append(c)

        left_node = RTreeNode(is_leaf=is_leaf, parent=node.parent)
        left_node.children = left_children
        left_node.compute_mbr()

        right_node = RTreeNode(is_leaf=is_leaf, parent=node.parent)
        right_node.children = right_children
        right_node.compute_mbr()

        # Set parent for child nodes if they are internal nodes
        if not is_leaf:
            for ch in left_node.children:
                ch['node'].parent = left_node
            for ch in right_node.children:
                ch['node'].parent = right_node

        return left_node, right_node

    def _pick_seeds(self, children):
        # Pick two children that are farthest apart on x dimension
        max_dist = -1
        seed1, seed2 = 0, 1
        for i in range(len(children)):
            for j in range(i+1, len(children)):
                dist = self._mbr_distance(children[i]['mbr'], children[j]['mbr'])
                if dist > max_dist:
                    max_dist = dist
                    seed1, seed2 = i, j
        return seed1, seed2

    def _mbr_distance(self, mbr1, mbr2):
        # Distance between two MBR centers (simple heuristic)
        x1 = (mbr1[0] + mbr1[2]) / 2.0
        y1 = (mbr1[1] + mbr1[3]) / 2.0
        x2 = (mbr2[0] + mbr2[2]) / 2.0
        y2 = (mbr2[1] + mbr2[3]) / 2.0
        return (x2 - x1)**2 + (y2 - y1)**2

    def _expansion(self, group, candidate):
        # Compute the area expansion if candidate is added to group
        mbrs = [c['mbr'] for c in group] + [candidate['mbr']]
        combined = self._combine_mbrs(mbrs)
        return self._area(combined) - self._area(self._combine_mbrs([c['mbr'] for c in group]))

    def _combine_mbrs(self, mbrs):
        xmins, ymins, xmaxs, ymaxs = zip(*mbrs)
        return [min(xmins), min(ymins), max(xmaxs), max(ymaxs)]

    def _area(self, mbr):
        return (mbr[2] - mbr[0]) * (mbr[3] - mbr[1])

    def _choose_leaf(self, node, mbr):
        if node.is_leaf:
            return node
        best_child = min(node.children, key=lambda child: self._enlargement(child['mbr'], mbr))
        return self._choose_leaf(best_child['node'], mbr)

    def _enlargement(self, parent_mbr, new_mbr):
        xmin = min(parent_mbr[0], new_mbr[0])
        ymin = min(parent_mbr[1], new_mbr[1])
        xmax = max(parent_mbr[2], new_mbr[2])
        ymax = max(parent_mbr[3], new_mbr[3])
        new_area = (xmax - xmin) * (ymax - ymin)
        current_area = (parent_mbr[2] - parent_mbr[0]) * (parent_mbr[3] - parent_mbr[1])
        return new_area - current_area

    def query(self, query_point, num_neighbors=1):
        import heapq
        candidate_nodes = []
        # Include an id() call on self.root to ensure uniqueness
        heapq.heappush(candidate_nodes, (0, id(self.root), self.root))

        nearest_neighbors = []

        while candidate_nodes:
            distance, _, node = heapq.heappop(candidate_nodes)  # Unpack the new tuple

            if node.is_leaf:
                for child in node.children:
                    dist = self._distance(query_point, child['mbr'])
                    if len(nearest_neighbors) < num_neighbors:
                        heapq.heappush(nearest_neighbors, (-dist, child['point']))
                    elif dist < -nearest_neighbors[0][0]:
                        heapq.heapreplace(nearest_neighbors, (-dist, child['point']))
            else:
                for child in node.children:
                    child_dist = self._distance(query_point, child['mbr'])
                    # Add a unique id for tie-breaking
                    if len(nearest_neighbors) < num_neighbors or child_dist < -nearest_neighbors[0][0]:
                        heapq.heappush(candidate_nodes, (child_dist, id(child['node']), child['node']))

        sorted_neighbors = sorted(nearest_neighbors, key=lambda x: -x[0])
        return [item[1] for item in sorted_neighbors]

    def _distance(self, query_point, mbr):
        if isinstance(query_point, DataPoint):
            x, y = query_point.longitude, query_point.latitude
        else:
            x, y = query_point
        xmin, ymin, xmax, ymax = mbr
        dx = max(0, xmin - x, x - xmax)
        dy = max(0, ymin - y, y - ymax)
        return dx*dx + dy*dy


if __name__ == "__main__":
    # Load the uszips.csv file
    file_path = os.path.join("data", "uszips.csv")
    data_points = DataIngestionFactory.load_data(file_path)

    # Create and populate the R-Tree
    rtree = RTree(max_children=4)
    rtree.insert(data_points)

    # Perform a sample query
    query_point = [-64.92, 18.34]  # Longitude, Latitude
    results = rtree.query(query_point, num_neighbors=5)

    print("Nearest Neighbors:")
    for result in results:
        print(f"Zip Code: {result.zip_code}, Location: ({result.latitude}, {result.longitude})")
        