import os
import osmium

from config import ROOT_DIR


class OSMHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.nodes = []

    def node(self, n):
        node_info = {
            "id": n.id,
            "latitude": n.location.lat,
            "longitude": n.location.lon,
            "tags": {tag.k: tag.v for tag in n.tags}
        }
        self.nodes.append(node_info)


if __name__ == '__main__':
    handler = OSMHandler()
    handler.apply_file(os.path.join(ROOT_DIR, 'data', 'us-virgin-islands-latest.osm.pbf'))

    for i, node in enumerate(handler.nodes):
        for key, value in node['tags'].items():
            if key:
                print(f"Node ID: {node['id']}, Location: ({node['latitude']}, {node['longitude']})")
                print("Tags:")
                print(f"  {key}: {value}")
                print("----------")
        
        # if i == 100:
        #     break
