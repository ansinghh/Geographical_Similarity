import unittest
from EC530.Geographic_Points import haversine_distance, convert_to_decimal, find_closest_points_haversine_kdtree

class TestMainFunctions(unittest.TestCase):
    def test_haversine_distance(self):
        # Test known points
        lat1, lon1 = 52.5200, 13.4050  # Berlin
        lat2, lon2 = 48.8566, 2.3522   # Paris
        expected_distance = 878  # Approximate distance in km
        result = round(haversine_distance(lat1, lon1, lat2, lon2))
        self.assertEqual(result, expected_distance)
    
    def test_convert_to_decimal_dd(self):
        # Test decimal degrees (DD)
        self.assertEqual(convert_to_decimal("52.5200N"), 52.5200)
        self.assertEqual(convert_to_decimal("13.4050E"), 13.4050)
        self.assertEqual(convert_to_decimal("-52.5200"), -52.5200)
    
    def test_convert_to_decimal_dms(self):
        # Test degrees, minutes, seconds (DMS)
        self.assertEqual(convert_to_decimal("52°31'12\"N"), 52.52)
        self.assertEqual(convert_to_decimal("13°24'18\"E"), 13.405)
        self.assertEqual(convert_to_decimal("52°31'12\"S"), -52.52)
    
    def test_find_closest_points_haversine_kdtree(self):
        # Test matching closest points
        array1 = [(52.52, 13.405)]  # Berlin
        array2 = [(48.8566, 2.3522), (51.5074, -0.1278)]  # Paris, London
        results = find_closest_points_haversine_kdtree(array1, array2)
        self.assertEqual(len(results), 1)
        self.assertAlmostEqual(results[0]["distance_km"], 878, delta=1)  # Approx distance Berlin-Paris

if __name__ == "__main__":
    unittest.main()
