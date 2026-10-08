from shapely.geometry import Point, LineString, Polygon

from app.services.measurement import calculate_measurement


def test_point_has_no_measurement():
    geometry = Point(76.2673, 9.9312)

    result = calculate_measurement(geometry)

    assert result["measurement_type"] is None
    assert result["value"] is None
    assert result["unit"] is None
    assert result["status"] == "no_measurement"


def test_linestring_returns_length():
    geometry = LineString([
        (76.2673, 9.9312),
        (76.2683, 9.9322)
    ])

    result = calculate_measurement(geometry)

    assert result["measurement_type"] == "length"
    assert result["value"] > 0
    assert result["unit"] == "metres"
    assert result["status"] == "success"


def test_polygon_returns_area():
    geometry = Polygon([
        (76.2673, 9.9312),
        (76.2683, 9.9312),
        (76.2683, 9.9322),
        (76.2673, 9.9322),
        (76.2673, 9.9312)
    ])

    result = calculate_measurement(geometry)

    assert result["measurement_type"] == "area"
    assert result["value"] > 0
    assert result["unit"] == "square_metres"
    assert result["status"] == "success"