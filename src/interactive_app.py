import tkinter as tk
from tkinter import ttk
import folium
import webbrowser
from data_importers import DataIngestionFactory, DataPoint
from lsh import MultiTableLSH
from kd_tree import ApproximateKDTree
from r_tree import RTree
import os

from config import SAMPLE_DATA


class InteractiveApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Geospatial Search App")

        # Input coordinates
        tk.Label(root, text="Lat (30 to 45):").grid(row=0, column=0)
        self.lat_entry = tk.Entry(root)
        self.lat_entry.insert(0, "42.360081") 
        self.lat_entry.grid(row=0, column=1)

        tk.Label(root, text="Long (-70 to -115):").grid(row=1, column=0)
        self.lon_entry = tk.Entry(root)
        self.lon_entry.insert(0, "-71.058884") 
        self.lon_entry.grid(row=1, column=1)

        # Algorithm selection
        tk.Label(root, text="Algorithm:").grid(row=2, column=0)
        self.algorithm_var = tk.StringVar()
        self.algorithm_menu = ttk.Combobox(root, textvariable=self.algorithm_var)
        self.algorithm_menu['values'] = ("Multi-Table LSH", "Approximate KD-Tree", "R-Tree")
        self.algorithm_menu.grid(row=2, column=1)
        self.algorithm_menu.current(0)

        # Run button
        self.run_button = tk.Button(root, text="Run", command=self.run_algorithm)
        self.run_button.grid(row=3, column=0, columnspan=2)

        # Load data and initialize algorithms
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
            # Get inputs
            lat = float(self.lat_entry.get())
            lon = float(self.lon_entry.get())
            algorithm_name = self.algorithm_var.get()

            # Create query point
            query_point = DataPoint(latitude=lat, longitude=lon, zip_code=None)

            print(f"Query Point: Latitude={query_point.latitude}, Longitude={query_point.longitude}")

            # Run selected algorithm
            algorithm = self.algorithms[algorithm_name]
            results = algorithm.query(query_point, num_neighbors=5)

            # Print results to console
            print("\nResults:")
            for i, result in enumerate(results, 1):
                print(f"Result {i}: Zip Code={result.zip_code}, Latitude={result.latitude}, Longitude={result.longitude}")

            # Generate map
            self.generate_map(query_point, results)
        except Exception as e:
            print(f"Error: {e}")

    def generate_map(self, query_point, results):
        # Create a map centered on the query point
        map_ = folium.Map(location=[query_point.latitude, query_point.longitude], zoom_start=12)

        # Add the query point, 
        # e.g. 18.34, -64.92
        # e.g. 42.360081, -71.058884
        folium.Marker([query_point.latitude, query_point.longitude], tooltip="Query Point", icon=folium.Icon(color="red")).add_to(map_)

        # Add results
        for result in results:
            folium.Marker([result.latitude, result.longitude], tooltip=f"Zip: {result.zip_code}", icon=folium.Icon(color="blue")).add_to(map_)

        # Save the map
        map_file = "map.html"
        map_.save(map_file)

        # Debug message
        print(f"Map saved as {map_file}")

        # Attempt to open the map in a browser
        try:
            print("Attempting to open map in a browser...")
            webbrowser.register(
                "firefox",
                None,
                webbrowser.BackgroundBrowser("/Applications/Firefox.app"),
            )
            browser = webbrowser.get("firefox")
            browser.open_new_tab(map_file)
            print("Browser should have opened.")
        except Exception as e:
            print(f"Error opening browser: {e}")
            print(f"Please open the map manually: {os.path.abspath(map_file)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = InteractiveApp(root)
    root.mainloop()
