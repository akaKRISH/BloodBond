import pytest
from app.services.geo_distance import calculate_haversine_distance


def test_haversine_same_point():
    # Distance between identical points is 0
    dist = calculate_haversine_distance(28.6139, 77.2090, 28.6139, 77.2090)
    assert dist == 0.0


def test_haversine_known_distance_delhi_to_mumbai():
    # Approx distance between Connaught Place Delhi (28.6315, 77.2167) and AIIMS Delhi (28.5672, 77.2100) ~ 7.2 km
    dist = calculate_haversine_distance(28.6315, 77.2167, 28.5672, 77.2100)
    assert 7.0 <= dist <= 7.5
