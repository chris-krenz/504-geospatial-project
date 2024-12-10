import osmium
import csv
import os


class DataPoint:
    def __init__(self, latitude: float, longitude: float, zip_code: str):
        self.latitude = latitude
        self.longitude = longitude
        self.zip_code = zip_code


class PBFToCSVConverter:
    def __init__(self, input_pbf: str, output_csv: str):
        self.input_pbf = input_pbf
        self.output_csv = output_csv

    class OSMHandler(osmium.SimpleHandler):
        def __init__(self):
            super().__init__()
            self.data_points = []

        def node(self, n):
            print(f"Node ID: {n.id}, Tags: {dict(n.tags)}")  # Log all tags for inspection
            if 'zip_code' in n.tags:  # Adjust this line if 'zip_code' is not the actual tag
                self.data_points.append(DataPoint(
                    latitude=n.location.lat,
                    longitude=n.location.lon,
                    zip_code=n.tags.get('zip_code')
                ))

    def convert(self):
        # Parse the PBF file
        handler = self.OSMHandler()
        print(f"Processing PBF file: {self.input_pbf}")
        handler.apply_file(self.input_pbf)

        # Write to CSV
        print(f"Writing to CSV file: {self.output_csv}")
        with open(self.output_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Write header
            writer.writerow(['latitude', 'longitude', 'zip_code'])
            # Write data
            for dp in handler.data_points:
                writer.writerow([dp.latitude, dp.longitude, dp.zip_code])

        print(f"Conversion completed. Output saved to {self.output_csv}")


if __name__ == "__main__":
    # Define input PBF and output CSV paths
    input_pbf_path = os.path.join("other_data", "us-virgin-islands-latest.osm.pbf")  # Update with your PBF file path
    output_csv_path = os.path.join("other_data", "us-virgin-islands-latest.csv")         # Desired output CSV file path

    # Convert PBF to CSV
    converter = PBFToCSVConverter(input_pbf=input_pbf_path, output_csv=output_csv_path)
    converter.convert()
