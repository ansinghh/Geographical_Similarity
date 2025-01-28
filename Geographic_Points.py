import math
import json
import csv
import re
import numpy as np
from scipy.spatial import cKDTree

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    
    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def convert_to_decimal(coord):
    # Function for converting coordinates to decimal
    coord = coord.strip()
    
    dms_regex = r"(\d+)\D*(\d+)?\D*(\d+(?:\.\d+)?)?\D*([NSEW])"
    ddm_regex = r"(\d+)\D*(\d+(?:\.\d+)?)\D*([NSEW])"
    dd_regex = r"(-?\d+(?:\.\d+)?)\D*([NSEW]?)"

    match_dms = re.match(dms_regex, coord)
    if match_dms:
        degrees, minutes, seconds, direction = match_dms.groups()
        decimal = float(degrees) + (float(minutes) / 60 if minutes else 0) + (float(seconds) / 3600 if seconds else 0)
        return -decimal if direction in "SW" else decimal

    match_ddm = re.match(ddm_regex, coord)
    if match_ddm:
        degrees, minutes, direction = match_ddm.groups()
        decimal = float(degrees) + float(minutes) / 60
        return -decimal if direction in "SW" else decimal

    match_dd = re.match(dd_regex, coord)
    if match_dd:
        decimal, direction = match_dd.groups()
        decimal = float(decimal)
        return -decimal if direction in "SW" else decimal

    raise ValueError(f"Unrecognized coordinate format: {coord}")

def read_csv(file_path, lat_col, lon_col):
    data = []
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)
        for row in reader:
            try:
                lat = convert_to_decimal(row[lat_col])
                lon = convert_to_decimal(row[lon_col])
                data.append((lat, lon))
            except (ValueError, IndexError) as e:
                print(f"Skipping invalid row in {file_path}: {row} - {e}")
                continue
    return data

def manual_input():
    # If the user decides to manually input coordinates
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
            print(f"Invalid input: {e}")
    return coordinates

def latlon_to_radians(lat_lon_list):
    return np.radians(lat_lon_list)

def find_closest_points_haversine_kdtree(array1, array2):
    if not array1 or not array2:
        print("Error: One of the input arrays is empty. Check file paths and column indices.")
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

def get_coordinates_input(prompt):
    while True:
        method = input(f"{prompt} Choose input method (csv/manual): ").strip().lower()
        if method == "csv":
            file_path = input("Enter CSV file path: ").strip()
            lat_col = int(input("Enter latitude column index (0-based): ").strip())
            lon_col = int(input("Enter longitude column index (0-based): ").strip())
            return read_csv(file_path, lat_col, lon_col)
        elif method == "manual":
            return manual_input()
        else:
            print("Invalid choice. Please enter 'csv' or 'manual'.")

def main():
    try:
        print("Input First Set of Coordinates: ")
        points1 = get_coordinates_input("First Set")

        print("\nInput Second Set of Coordinates: ")
        points2 = get_coordinates_input("Second Set")

        if not points1 or not points2:
            print("Error: One of the input sets has no valid coordinate data.")
            return

        results = find_closest_points_haversine_kdtree(points1, points2)

        if not results:
            print("No valid matches found.")
            return

        output_type = input("Enter output format (print/json): ").strip().lower() # Choose to save the output in a consolidated JSON to read easily or to print in the command line
        if output_type == "json":
            output_file = input("Enter output file name: ").strip()
            with open(output_file, "w", encoding="utf-8") as outfile:
                json.dump(results, outfile, indent=4)
            print(f"Results saved to {output_file}")
        else:
            for result in results:
                print(result)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
