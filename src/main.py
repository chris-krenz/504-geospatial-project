"""
Main script for the program.  (For now, just runs benchmark.py).
"""

from utils import logger
from benchmark import sample_data_benchmark


def main():

    print('\nStarting program...')

    logger.config_logger()

    sample_data_benchmark()


if __name__ == '__main__':
    main()
