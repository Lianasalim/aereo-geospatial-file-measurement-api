import math

import geopandas as gpd


def make_json_safe(value):
    """
    Convert values that cannot be represented in standard JSON
    into JSON-compatible values.
    """

    if value is None:
        return None

    # Handle missing Pandas values such as NaN and NaT
    try:
        if value != value:
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None

    # Convert Pandas/Numpy scalar values to native Python values
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, TypeError):
            pass

    return value


def calculate_measurement(geometry) -> dict:
    geometry_type = geometry.geom_type

    if geometry_type == "Point":
        return {
            "measurement_type": None,
            "value": None,
            "unit": None,
            "status": "no_measurement"
        }

    if geometry_type == "LineString":
        return {
            "measurement_type": "length",
            "value": float(geometry.length),
            "unit": "metres",
            "status": "success"
        }

    if geometry_type == "Polygon":
        return {
            "measurement_type": "area",
            "value": float(geometry.area),
            "unit": "square_metres",
            "status": "success"
        }

    return {
        "measurement_type": None,
        "value": None,
        "unit": None,
        "status": "unsupported_geometry"
    }


def calculate_measurements(gdf: gpd.GeoDataFrame) -> list:
    results = []

    for index, row in gdf.iterrows():
        geometry = row.geometry

        measurement = calculate_measurement(geometry)

        properties = {
            key: make_json_safe(value)
            for key, value in row.items()
            if key != "geometry"
        }

        geometry_geojson = geometry.__geo_interface__

        results.append({
            "feature_index": index,
            "geometry_type": geometry.geom_type,
            "geometry": geometry_geojson,
            "properties": properties,
            **measurement
        })

    return results