from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile, BadZipFile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.file_processor import read_geospatial_file
from app.services.crs_handler import prepare_for_measurement
from app.services.measurement import calculate_measurements


router = APIRouter(prefix="/api/files", tags=["Files"])

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".kml", ".zip"}

# Temporary in-memory storage
file_registry = {}


def validate_shapefile_zip(file_path: Path) -> None:
    """
    Validate that a ZIP archive contains the required
    Shapefile components.
    """

    try:
        with ZipFile(file_path, "r") as zip_file:
            files = zip_file.namelist()

    except BadZipFile:
        raise ValueError(
            "Uploaded ZIP file is not a valid ZIP archive."
        )

    # Ignore directory entries
    file_names = [
        Path(name).name.lower()
        for name in files
        if not name.endswith("/")
    ]

    required_components = {".shp", ".shx", ".dbf", ".prj"}

    available_components = {
        Path(name).suffix.lower()
        for name in file_names
    }

    missing_components = required_components - available_components

    if missing_components:
        missing = ", ".join(sorted(missing_components))
        raise ValueError(
            f"Invalid Shapefile ZIP. Missing required component(s): {missing}"
        )


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a KML file or Shapefile ZIP.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only KML files and Shapefile ZIP files are supported."
        )

    file_id = str(uuid4())
    saved_filename = f"{file_id}{extension}"
    file_path = UPLOAD_DIR / saved_filename

    try:
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Validate Shapefile ZIP
        if extension == ".zip":
            validate_shapefile_zip(file_path)

        file_registry[file_id] = {
            "file_id": file_id,
            "filename": file.filename,
            "file_type": extension.lstrip("."),
            "file_path": str(file_path),
            "status": "uploaded",
        }

        return {
            "file_id": file_id,
            "filename": file.filename,
            "file_type": extension.lstrip("."),
            "status": "uploaded",
        }

    except ValueError as exc:
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to save or validate file: {str(exc)}"
        )


@router.get("/{file_id}")
async def get_file(file_id: str):
    """
    Get metadata for an uploaded file.
    """

    if file_id not in file_registry:
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    return file_registry[file_id]


@router.get("/{file_id}/measurements/")
async def get_measurements(file_id: str):
    """
    Extract geometries and calculate measurements
    for an uploaded geospatial file.
    """

    if file_id not in file_registry:
        raise HTTPException(
            status_code=404,
            detail="File not found."
        )

    file_info = file_registry[file_id]

    try:
        # Step 1: Read the uploaded geospatial file
        gdf = read_geospatial_file(
            file_info["file_path"],
            file_info["file_type"]
        )

        # Keep the original geometry and CRS
        original_gdf = gdf.copy()

        # Step 2: Prepare CRS for accurate measurements
        measurement_gdf = prepare_for_measurement(gdf)

        # Step 3: Calculate measurements using projected CRS
        measurements = calculate_measurements(measurement_gdf)

        # Return original geometry instead of projected geometry
        for original_row, measurement in zip(
            original_gdf.itertuples(),
            measurements
        ):
            measurement["geometry"] = (
                original_row.geometry.__geo_interface__
            )

        return {
            "file_id": file_id,
            "filename": file_info["filename"],
            "source_crs": str(gdf.crs),
            "measurement_crs": str(measurement_gdf.crs),
            "feature_count": len(gdf),
            "measurements": measurements,
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Uploaded file could not be found."
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process geospatial file: {str(exc)}"
        )