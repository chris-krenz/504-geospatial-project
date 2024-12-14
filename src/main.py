"""
Main script for the program.  (For now, just runs benchmark.py).
"""

from utils import logger
from benchmark import sample_data_benchmark


def main():

    print('\nStarting program...')

    logger.config_logger()

    print('\nRunning benchmark...')

    sample_data_benchmark()

    print('\nResults printed. Suggest running the app.py script next for an interactive experience.')

    print('\nProgram complete.')


if __name__ == '__main__':
    main()
