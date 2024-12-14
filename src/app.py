"""
Run this script to open a window that will allow you specify coords and an algo. 
Upon running the script, a map will be generated (in the root directory) and open in your browser.
(If the map doesn't open automatically, please open the map.html file manually.)
NOTE: Strongly recommended to run with Python 3.11 (or perhaps later).
    For earlier versions of Python, you may find the window appears blank.
The app is NOT run via Docker (getting Tkinter to work in Docker is tricky...).
"""

import tkinter as tk
from tkinter import ttk
import folium
import webbrowser
import os

from data_importers import DataIngestionFactory, DataPoint
from lsh import MultiTableLSH
from kd_tree import ApproximateKDTree
from r_tree import RTree

from config import SAMPLE_DATA


class InteractiveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Geospatial Search App")
        self.root.geometry("500x250")

        instructions = ("Enter coords, select algo, press Run, and a map should open in your browser.\n\n")
        tk.Label(root, text=instructions, justify="left").grid(row=0, column=0, columnspan=2, pady=5)

        # Input coords
        tk.Label(root, text="Lat (30 to 45):").grid(row=1, column=0)
        self.lat_entry = tk.Entry(root)
        self.lat_entry.insert(0, "42.360081") 
        self.lat_entry.grid(row=1, column=1)

        tk.Label(root, text="Long (-70 to -115):").grid(row=2, column=0)
        self.lon_entry = tk.Entry(root)
        self.lon_entry.insert(0, "-71.058884") 
        self.lon_entry.grid(row=2, column=1)

        # algo selection
        tk.Label(root, text="Algorithm:").grid(row=3, column=0, sticky='w')
        self.algorithm_var = tk.StringVar(value="Multi-Table LSH")

        algorithms = ["Multi-Table LSH", "Approximate KD-Tree", "R-Tree"]
        for i, algo in enumerate(algorithms):
            tk.Radiobutton(
                root,
                text=algo,
                variable=self.algorithm_var,
                value=algo
            ).grid(row=3+i, column=0, columnspan=2, sticky='w')

        # 'Run'
        self.run_button = tk.Button(root, text="Run", command=self.run_algorithm)
        self.run_button.grid(row=3+len(algorithms), column=0, columnspan=2)

        # load data and init algos
        self.data_points = self.load_data()
        self.algorithms = {
            "Multi-Table LSH": self.init_lsh(),
            "Approximate KD-Tree": self.init_kd_tree(),
            "R-Tree": self.init_r_tree()
        }

    def load_data(self):
        file_path = os.path.join(SAMPLE_DATA)
        return DataIngestionFactory.load_data(file_path)

    def init_lsh(self):
        lsh = MultiTableLSH(num_tables=3, hash_size=2)
        lsh.insert(self.data_points)
        return lsh

    def init_kd_tree(self):
        return ApproximateKDTree(self.data_points, max_depth=10)

    def init_r_tree(self):
        r_tree = RTree()
        r_tree.insert(self.data_points)
        return r_tree

    def run_algorithm(self):
        try:
            # get inputs
            lat = float(self.lat_entry.get())
            lon = float(self.lon_entry.get())
            algorithm_name = self.algorithm_var.get()

            # Create target point
            query_point = DataPoint(latitude=lat, longitude=lon, zip_code=None)

            print(f"Query Point: Latitude={query_point.latitude}, Longitude={query_point.longitude}")

            # Run algo
            algorithm = self.algorithms[algorithm_name]
            results = algorithm.query(query_point, num_neighbors=5)

            # Print results...
            print("\nResults:")
            for i, result in enumerate(results, 1):
                print(f"Result {i}: Zip Code={result.zip_code}, Latitude={result.latitude}, Longitude={result.longitude}")

            # Gen map file (i.e. map.html in the root folder...)
            self.generate_map(query_point, results)
        except Exception as e:
            print(f"Error: {e}")

    def generate_map(self, query_point, results):
        # create map at targte pt
        map_ = folium.Map(location=[query_point.latitude, query_point.longitude], zoom_start=12)
        folium.Marker(
            [query_point.latitude, query_point.longitude],
            tooltip="Query Point", 
            icon=folium.Icon(color="red")
        ).add_to(map_)

        # Add results (i.e. zip codes markers)
        for result in results:
            folium.Marker(
                [result.latitude, result.longitude],
                tooltip=f"Zip: {result.zip_code}",
                icon=folium.Icon(color="blue")
            ).add_to(map_)

        # Save map
        map_file = "map.html"
        map_.save(map_file)
        print(f"Map saved as {map_file}")

        # Open the map in the default browser
        # NOTE: If this doesn't work, please just open the file manually...
        # It should update each time you run the app...
        map_path = os.path.abspath(map_file)
        webbrowser.open("file://" + map_path)


if __name__ == "__main__":
    root = tk.Tk()
    app = InteractiveApp(root)
    root.mainloop()
