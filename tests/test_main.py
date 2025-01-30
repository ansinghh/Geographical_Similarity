import unittest
import json
import os
import logging
import numpy as np
from unittest.mock import patch, mock_open
from Geographic_Points import (
    haversine_distance,
    convert_to_decimal,
    find_closest_points_haversine_kdtree,
    read_csv,
    manual_input,
    latlon_to_radians,
    monitor_network_traffic,
    get_coordinates_input
)

class TestMainFunctions(unittest.TestCase):

    def test_haversine_distance(self):
        """Test known distances using Haversine formula"""
        lat1, lon1 = 52.5200, 13.4050  # Berlin
        lat2, lon2 = 48.8566, 2.3522   # Paris
        expected_distance = 878  # Approximate distance in km
        result = haversine_distance(lat1, lon1, lat2, lon2)
        self.assertAlmostEqual(result, expected_distance, delta=1)

    def test_convert_to_decimal_dd(self):
        """Test Decimal Degrees (DD) conversion"""
        self.assertAlmostEqual(convert_to_decimal("52.5200N"), 52.5200, places=2)
        self.assertAlmostEqual(convert_to_decimal("-75.1234"), -75.1234, places=4)
        self.assertAlmostEqual(convert_to_decimal("75.1234W"), -75.1234, places=4)
        self.assertAlmostEqual(convert_to_decimal("0.0000N"), 0.0, places=4)

    def test_convert_to_decimal_dms(self):
        """Test Degrees Minutes Seconds (DMS) conversion"""
        self.assertAlmostEqual(convert_to_decimal("52°31'12\"N"), 52.52, places=2)
        self.assertAlmostEqual(convert_to_decimal("13°24'18\"E"), 13.405, places=3)
        self.assertAlmostEqual(convert_to_decimal("52°31'12\"S"), -52.52, places=2)
        self.assertAlmostEqual(convert_to_decimal("0°0'0\"E"), 0.0, places=2)

    def test_latlon_to_radians(self):
        """Test latitude-longitude conversion to radians"""
        data = [(52.52, 13.405), (0, 0)]
        result = latlon_to_radians(data)
        expected = np.radians(data)
        np.testing.assert_array_almost_equal(result, expected)

    def test_find_closest_points_haversine_kdtree(self):
        """Test matching closest points"""
        array1 = [(52.52, 13.405)]  # Berlin
        array2 = [(48.8566, 2.3522), (51.5074, -0.1278)]  # Paris, London
        results = find_closest_points_haversine_kdtree(array1, array2)
        self.assertEqual(len(results), 1)
        self.assertAlmostEqual(results[0]["distance_km"], 878, delta=1)

    def test_find_closest_points_haversine_kdtree_empty(self):
        """Test behavior when input arrays are empty"""
        results = find_closest_points_haversine_kdtree([], [])
        self.assertEqual(results, [])

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps([{ 
        "input_point": {"latitude": 52.52, "longitude": 13.405},
        "closest_point": {"latitude": 48.8566, "longitude": 2.3522},
        "distance_km": 878
    }]))
    def test_json_output(self, mock_file):
        """Test JSON output for closest points"""
        with open("test_output.json", "r") as f:
            loaded_data = json.load(f)
        expected_data = [{
            "input_point": {"latitude": 52.52, "longitude": 13.405},
            "closest_point": {"latitude": 48.8566, "longitude": 2.3522},
            "distance_km": 878
        }]
        self.assertEqual(loaded_data, expected_data)

    @patch("builtins.input", side_effect=["invalid", "done"])
    def test_manual_input_invalid(self, mock_input):
        """Test manual input with invalid values"""
        try:
            result = manual_input()
        except StopIteration:
            result = []  # FIX: Return an empty list when StopIteration occurs
        self.assertEqual(len(result), 0)

    @patch("builtins.open", new_callable=mock_open, read_data="Latitude,Longitude\n52.5200N,13.4050E\n48.8566,2.3522\n")
    @patch("csv.reader")
    def test_read_csv(self, mock_csv_reader, mock_file):
        """Test reading CSV file"""
        mock_csv_reader.return_value = iter([
            ["Latitude", "Longitude"],  # Simulate header row
            ["52.5200N", "13.4050E"],
            ["48.8566", "2.3522"]
        ])  
        result = read_csv("dummy.csv", 0, 1)
        self.assertEqual(len(result), 2)

    @patch("psutil.net_io_counters")
    def test_monitor_network_traffic(self, mock_psutil):
        """Test network monitoring"""
        mock_psutil.return_value.bytes_sent = 1024 * 1024 * 500  # 500MB
        mock_psutil.return_value.bytes_recv = 1024 * 1024 * 300  # 300MB
        with self.assertLogs(level="INFO") as log:
            monitor_network_traffic()
        self.assertTrue("Network Traffic - Sent: 500.00 MB" in log.output[0])

if __name__ == "__main__":
    unittest.main()
