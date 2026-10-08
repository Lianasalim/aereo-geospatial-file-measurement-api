from io import BytesIO

from fastapi.testclient import TestClient

from app.main import app
from app.api.routes.files import file_registry


client = TestClient(app)


def test_upload_kml_file():
    kml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <Document>
        <Placemark>
            <name>Test Point</name>
            <Point>
                <coordinates>76.2673,9.9312,0</coordinates>
            </Point>
        </Placemark>
    </Document>
</kml>
"""

    response = client.post(
        "/api/files/",
        files={
            "file": (
                "test.kml",
                BytesIO(kml_content),
                "application/vnd.google-earth.kml+xml",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "file_id" in data
    assert data["filename"] == "test.kml"
    assert data["file_type"] == "kml"
    assert data["status"] == "uploaded"

    # Clean up test registry entry
    file_registry.pop(data["file_id"], None)


def test_reject_unsupported_file_type():
    response = client.post(
        "/api/files/",
        files={
            "file": (
                "test.txt",
                BytesIO(b"invalid file"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert "Only KML files" in response.json()["detail"]


def test_get_missing_file_returns_404():
    response = client.get(
        "/api/files/non-existent-file"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "File not found."