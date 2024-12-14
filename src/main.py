"""
Run this script to run both: 
  - the benchmarking script (benchmark.py) and
  - the interactive app (app.py)
"""

from utils import logger
from benchmark import sample_data_benchmark
import tkinter as tk
from app import InteractiveApp


def main():
    print('\nStarting program...')

    logger.config_logger()

    print('\nRunning benchmark...')
    sample_data_benchmark()

    print('\nRunning interactive app...')
    root = tk.Tk()
    app = InteractiveApp(root)
    root.mainloop()

    print('\nProgram complete.')


if __name__ == '__main__':
    main()
