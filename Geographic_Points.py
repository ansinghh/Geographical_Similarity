import math
import json
import csv
import re
import numpy as np
import tracemalloc
import cProfile
import psutil
import logging
from scipy.spatial import cKDTree

# Configure logging
logging.basicConfig(
    filename="app.log", 
    filemode="w", 
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Enable memory tracking
tracemalloc.start()
logging.info("Memory profiling started.")

def haversine_distance(lat1, lon1, lat2, lon2):
    logging.info(f"Calculating Haversine distance between ({lat1}, {lon1}) and ({lat2}, {lon2})")
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    logging.info(f"Computed distance: {distance:.2f} km")
    return distance

def convert_to_decimal(coord):
    coord = coord.strip()
    logging.info(f"Converting coordinate: {coord}")

    dms_regex = r"^(\d+)[°dD]?\s*(\d+)?[′']?\s*(\d+(?:\.\d+)?)?[″\"]?\s*([NSEW])$"
    ddm_regex = r"^(\d+)[°dD]?\s*(\d+(?:\.\d+)?)?[′']?\s*([NSEW])$"
    dd_regex = r"^(-?\d+(?:\.\d+)?)\s*([NSEW]?)$"

    if re.match(dd_regex, coord):
        match = re.match(dd_regex, coord)
        decimal, direction = match.groups()
        decimal = float(decimal)
        return -decimal if direction in ("S", "W") else decimal

    elif re.match(ddm_regex, coord):
        match = re.match(ddm_regex, coord)
        degrees, minutes, direction = match.groups()
        decimal = float(degrees) + (float(minutes) / 60 if minutes else 0)
        return -decimal if direction in ("S", "W") else decimal

    elif re.match(dms_regex, coord):
        match = re.match(dms_regex, coord)
        degrees, minutes, seconds, direction = match.groups()
        decimal = (
            float(degrees) + 
            (float(minutes) / 60 if minutes else 0) + 
            (float(seconds) / 3600 if seconds else 0)
        )
        return -decimal if direction in ("S", "W") else decimal

    logging.warning(f"Invalid coordinate format: {coord}")
    raise ValueError(f"Unrecognized coordinate format: {coord}")

def read_csv(file_path, lat_col, lon_col):
    data = []
    logging.info(f"Reading CSV file: {file_path}")
    try:
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            for row in reader:
                try:
                    lat = convert_to_decimal(row[lat_col])
                    lon = convert_to_decimal(row[lon_col])
                    data.append((lat, lon))
                except (ValueError, IndexError) as e:
                    logging.warning(f"Skipping invalid row in {file_path}: {row} - {e}")
                    continue
        return data
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return []

def latlon_to_radians(lat_lon_list):
    return np.radians(lat_lon_list)

def find_closest_points_haversine_kdtree(array1, array2):
    if not array1 or not array2:
        logging.error("Error: One of the input arrays is empty.")
        return []

    array1_rad = latlon_to_radians(array1)
    array2_rad = latlon_to_radians(array2)
    tree = cKDTree(array2_rad)
    distances, indices = tree.query(array1_rad, p=2)

    results = []
    for i, index in enumerate(indices):
        lat1, lon1 = array1[i]
        lat2, lon2 = array2[index]
        haversine_dist = haversine_distance(lat1, lon1, lat2, lon2)
        results.append({
            "input_point": {"latitude": lat1, "longitude": lon1},
            "closest_point": {"latitude": lat2, "longitude": lon2},
            "distance_km": round(haversine_dist, 2),
        })
    return results

def monitor_network_traffic():
    net_io = psutil.net_io_counters()
    logging.info(f"Network Traffic - Sent: {net_io.bytes_sent / (1024 * 1024):.2f} MB, "
                 f"Received: {net_io.bytes_recv / (1024 * 1024):.2f} MB")

def manual_input():
    coordinates = []
    print("Enter coordinates one by one in any format (DD, DMS, DDM). Type 'done' to finish:")
    while True:
        lat = input("Enter latitude (or 'done' to finish): ").strip()
        if lat.lower() == "done":
            break
        lon = input("Enter longitude: ").strip()
        try:
            lat_dec = convert_to_decimal(lat)
            lon_dec = convert_to_decimal(lon)
            coordinates.append((lat_dec, lon_dec))
        except ValueError as e:
            logging.warning(f"Invalid input: {e}")
            print(f"Invalid input: {e}")
    return coordinates

def get_coordinates_input(prompt):
    logging.info(f"Prompting user for {prompt} coordinate input method.")
    
    while True:
        method = input(f"{prompt} Choose input method (csv/manual): ").strip().lower()

        if method == "csv":
            file_path = input("Enter CSV file path: ").strip()
            lat_col = int(input("Enter latitude column index (0-based): ").strip())
            lon_col = int(input("Enter longitude column index (0-based): ").strip())
            return read_csv(file_path, lat_col, lon_col)

        elif method == "manual":
            logging.info(f"User chose manual entry for {prompt} coordinates.")
            return manual_input()

        else:
            logging.warning(f"Invalid input method: {method}. User must enter 'csv' or 'manual'.")
            print("Invalid choice. Please enter 'csv' or 'manual'.")

def main():
    logging.info("Program started.")
    
    # Start CPU profiling
    profiler = cProfile.Profile()
    profiler.enable()

    points1 = get_coordinates_input("First Set")
    points2 = get_coordinates_input("Second Set")

    if not points1 or not points2:
        logging.error("No valid coordinate data found.")
        print("Error: One of the input sets has no valid coordinate data.")
        return

    results = find_closest_points_haversine_kdtree(points1, points2)

    if not results:
        logging.warning("No valid matches found.")
        print("No valid matches found.")
        return

    output_type = input("Enter output format (print/json): ").strip().lower()
    if output_type == "json":
        output_file = input("Enter output file name: ").strip()
        with open(output_file, "w", encoding="utf-8") as outfile:
            json.dump(results, outfile, indent=4)
        logging.info(f"Results saved to {output_file}")
        print(f"Results saved to {output_file}")
    else:
        for result in results:
            print(result)

    monitor_network_traffic()

    # Stop CPU profiling and print results
    profiler.disable()
    profiler.print_stats(sort="cumulative")

if __name__ == "__main__":
    main()
