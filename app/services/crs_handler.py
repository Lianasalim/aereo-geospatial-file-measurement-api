import geopandas as gpd


def prepare_for_measurement(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Prepare a GeoDataFrame for accurate metric measurements.

    If the input CRS is geographic (for example EPSG:4326),
    automatically transform it to a suitable projected CRS.
    """

    if gdf.crs is None:
        raise ValueError(
            "Input file does not contain a coordinate reference system (CRS)."
        )

    if gdf.crs.is_geographic:
        # Estimate a suitable local projected CRS.
        projected_crs = gdf.estimate_utm_crs()

        if projected_crs is None:
            raise ValueError(
                "Unable to determine a suitable projected CRS for measurement."
            )

        return gdf.to_crs(projected_crs)

    return gdf