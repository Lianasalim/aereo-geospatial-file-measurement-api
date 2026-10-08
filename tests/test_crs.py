import geopandas as gpd
from shapely.geometry import Polygon

from app.services.crs_handler import prepare_for_measurement


def test_geographic_crs_is_projected():
    gdf = gpd.GeoDataFrame(
        {
            "Name": ["Test Polygon"],
            "geometry": [
                Polygon([
                    (76.2673, 9.9312),
                    (76.2683, 9.9312),
                    (76.2683, 9.9322),
                    (76.2673, 9.9322),
                    (76.2673, 9.9312)
                ])
            ]
        },
        crs="EPSG:4326"
    )

    result = prepare_for_measurement(gdf)

    assert result.crs is not None
    assert result.crs.is_projected
    assert result.crs.to_epsg() == 32643


def test_projected_crs_is_kept():
    gdf = gpd.GeoDataFrame(
        {
            "Name": ["Test Polygon"],
            "geometry": [
                Polygon([
                    (638900, 1098000),
                    (639000, 1098000),
                    (639000, 1098100),
                    (638900, 1098100),
                    (638900, 1098000)
                ])
            ]
        },
        crs="EPSG:32643"
    )

    result = prepare_for_measurement(gdf)

    assert result.crs.to_epsg() == 32643