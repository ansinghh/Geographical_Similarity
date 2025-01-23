import math

# For calculating the similarity between points in two different arrays I considered euclidean
# however it is not the most accurate way of finding similar coordinates in a geographical setting
# Hence, upon some research, I came across the haversine distance formula which measures the 
# angular distance between two points on the surface of a sphere.
# Here is the source I used to help me implement the solution: https://nathan.fun/posts/2016-09-07/haversine-with-python/

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth (km)
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    change_in_longitude = lat2 - lat1
    change_in_latitude = lon2 - lon1

    a = math.sin(change_in_latitude / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(change_in_longitude / 2) ** 2
    a = min(1, max(0, a)) # Restricts a to be [0,1]
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def find_closest_points(array1, array2):
    results = []
    for lat1, lon1 in array1:
        closest_point = None
        min_distance = float('inf')
        for lat2, lon2 in array2:
            distance = haversine_distance(lat1, lon1, lat2, lon2)
            if distance < min_distance:
                min_distance = distance
                closest_point = (lat2, lon2)
        results.append(((lat1, lon1), closest_point))
    return results

# Testing Similarities based on different longitudes and latitudes
array1 = [
    (40.7128, -74.0060),  # New York, USA
    (48.8566, 2.3522),    # Paris, France
    (-33.8688, 151.2093), # Sydney, Australia
    (35.6895, 139.6917),  # Tokyo, Japan
    (55.7558, 37.6173),   # Moscow, Russia
]

array2 = [
    (34.0522, -118.2437), # Los Angeles, USA
    (51.5074, -0.1278),   # London, UK
    (19.0760, 72.8777),   # Mumbai, India
    (39.9042, 116.4074),  # Beijing, China
    (-23.5505, -46.6333), # São Paulo, Brazil
]

matches = find_closest_points(array1, array2)

for match in matches:
    print(f"Point {match[0]} is closest to {match[1]}")

