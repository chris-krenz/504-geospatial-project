"""
Configuration to specify file paths and other variables.
"""

import os

ROOT_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLE_DATA = os.path.join(ROOT_DIR, 'data', 'uszips.csv')
