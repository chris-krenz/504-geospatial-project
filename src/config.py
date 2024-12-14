import os

ROOT_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_DATA = os.path.join(ROOT_DIR, 'data', 'uszips.csv')
OSM_DATA    = os.path.join(ROOT_DIR, 'other_data', 'us-northeast-latest.osm.pbf')
