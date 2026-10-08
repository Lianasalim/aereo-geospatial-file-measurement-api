from pathlib import Path

import geopandas as gpd


def read_geospatial_file(file_path: str, file_type: str) -> gpd.GeoDataFrame:
    """
    Read a supported geospatial file and return a GeoDataFrame.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError("Geospatial file not found.")

    if file_type == "kml":
        return gpd.read_file(path, driver="KML")

    if file_type == "zip":
        return gpd.read_file(f"zip://{path}")

    raise ValueError(
        f"Unsupported file type: {file_type}"
    )