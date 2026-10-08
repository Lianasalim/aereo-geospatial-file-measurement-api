\# Geospatial File Measurement API



A FastAPI-based backend for uploading and processing geospatial files in KML and Shapefile ZIP formats. The API extracts geospatial features, geometry, CRS, and properties, and calculates measurements such as polygon area and LineString length.



\## Features



\- Upload KML files

\- Upload Shapefile ZIP archives

\- Validate Shapefile components

\- Extract geometry and feature properties

\- Detect the source Coordinate Reference System (CRS)

\- Automatically project geographic CRS data for accurate measurements

\- Calculate Polygon area

\- Calculate LineString length

\- Handle Point geometries without measurement

\- Return original geometry in the source CRS

\- REST API with Swagger documentation

\- Automated tests using pytest



\## Technology Stack



\- Python 3.11

\- FastAPI

\- Uvicorn

\- GeoPandas

\- Shapely

\- PyProj

\- Pytest



\## Project Structure



```text

aereo-geospatial-api/

│

├── app/

│   ├── api/

│   │   └── routes/

│   │       └── files.py

│   │

│   ├── core/

│   │   └── config.py

│   │

│   ├── models/

│   │   └── file.py

│   │

│   ├── schemas/

│   │   └── file.py

│   │

│   ├── services/

│   │   ├── crs\_handler.py

│   │   ├── file\_processor.py

│   │   └── measurement.py

│   │

│   ├── utils/

│   │   └── validators.py

│   │

│   └── main.py

│

├── tests/

│   ├── test\_crs.py

│   ├── test\_measurements.py

│   └── test\_upload.py

│

├── data/

│   └── .gitkeep

│

├── .gitignore

├── requirements.txt

└── README.md



Installation

1\. Clone the repository

git clone https://github.com/<your-username>/aereo-geospatial-api.git

cd aereo-geospatial-api



2\. Create a virtual environment

python -m venv .venv



3\. Activate the virtual environment

Windows PowerShell:

.\\.venv\\Scripts\\Activate.ps1



4\. Install dependencies

pip install -r requirements.txt



Running the API

Start the development server:

uvicorn app.main:app --reload



The API will be available at:

http://127.0.0.1:8000



Interactive Swagger documentation:

http://127.0.0.1:8000/docs



API Endpoints

Upload a file

POST /api/files/



Accepts:

\- .kml

\- Shapefile .zip

For Shapefile ZIP uploads, the archive must contain:

.shp

.shx

.dbf

.prj



Example response:

{

&#x20; "file\_id": "example-file-id",

&#x20; "filename": "example.kml",

&#x20; "file\_type": "kml",

&#x20; "status": "uploaded"

}



Get file metadata

GET /api/files/{file\_id}



Returns metadata associated with the uploaded file.

Calculate measurements

GET /api/files/{file\_id}/measurements/



Returns:

\- Source CRS

\- Measurement CRS

\- Feature count

\- Feature geometry

\- Feature properties

\- Geometry type

\- Measurement type

\- Measurement value

\- Measurement unit

\- Processing status

Geometry Measurements

Geometry Type	Measurement

Point	No measurement

LineString	Length

Polygon	Area

Other/unsupported	Gracefully reported as unsupported





Example

For a Polygon:

{

&#x20; "geometry\_type": "Polygon",

&#x20; "measurement\_type": "area",

&#x20; "value": 12125.53,

&#x20; "unit": "square\_metres",

&#x20; "status": "success"

}



For a LineString:

{

&#x20; "geometry\_type": "LineString",

&#x20; "measurement\_type": "length",

&#x20; "value": 155.73,

&#x20; "unit": "metres",

&#x20; "status": "success"

}



For a Point:

{

&#x20; "geometry\_type": "Point",

&#x20; "measurement\_type": null,

&#x20; "value": null,

&#x20; "unit": null,

&#x20; "status": "no\_measurement"

}



CRS Handling

Accurate area and distance calculations should not be performed directly on geographic coordinates such as latitude and longitude.

For example, an uploaded KML may use:

EPSG:4326



When the input CRS is geographic, the application automatically estimates a suitable projected CRS and transforms the data before calculating measurements.

Example:

Source CRS

EPSG:4326

&#x20;    │

&#x20;    ▼

Projected CRS

EPSG:32643

&#x20;    │

&#x20;    ▼

Measurement calculation



The original geometry is preserved in the API response, while the projected geometry is used internally for measurement calculations.

Processing Flow

Upload File

&#x20;    │

&#x20;    ▼

Validate File Type

&#x20;    │

&#x20;    ├── KML

&#x20;    │

&#x20;    └── Shapefile ZIP

&#x20;             │

&#x20;             ▼

&#x20;      Validate Shapefile

&#x20;      .shp/.shx/.dbf/.prj

&#x20;             │

&#x20;             ▼

&#x20;     Read with GeoPandas

&#x20;             │

&#x20;             ▼

&#x20;      Detect Source CRS

&#x20;             │

&#x20;             ▼

&#x20;     Prepare Measurement CRS

&#x20;             │

&#x20;             ▼

&#x20;     Calculate Measurements

&#x20;             │

&#x20;             ▼

&#x20;     Return JSON Response



\## Architecture

The application separates responsibilities into different layers.

API Layer

app/api/routes/files.py

Handles:

\- File uploads

\- File metadata requests

\- Measurement requests

\- HTTP error responses

File Processing Layer

app/services/file\_processor.py

Handles reading supported geospatial formats using GeoPandas.

CRS Layer

app/services/crs\_handler.py

Handles CRS validation and transformation for measurement purposes.

Measurement Layer

app/services/measurement.py

Handles geometry-specific measurement calculations.

Testing Layer

tests/

Contains automated tests for:

\- Measurement calculations

\- CRS handling

\- API upload behavior

\- API error handling

Design Decisions

Projected CRS for measurements

Area and distance calculations are performed using a projected CRS rather than directly using geographic latitude/longitude coordinates.

This improves measurement accuracy and avoids treating angular coordinate units as linear units.

Original geometry preservation

The source geometry is retained for the API response. Projection is used only for internal measurement calculations.

This allows consumers of the API to receive geometry in the original source CRS while still obtaining measurements in metric units.

Shapefile validation

A Shapefile is composed of multiple files. The API validates that uploaded ZIP archives contain the essential components:

.shp

.shx

.dbf

.prj



Invalid ZIP files are rejected before geospatial processing.

Temporary file registry

Uploaded file metadata is currently stored in an in-memory registry for simplicity.

This keeps the assignment implementation lightweight and avoids unnecessary database complexity.

Running Tests

Run the complete test suite with:

pytest -q



\## Current test coverage includes:

\- Point measurement behavior

\- LineString length calculation

\- Polygon area calculation

\- Geographic CRS projection

\- Projected CRS preservation

\- KML upload

\- Unsupported file rejection

\- Missing file handling



\## Learning Outcomes

This project provided practical experience with:

\- FastAPI REST API development

\- Multipart file uploads

\- Geospatial data processing with GeoPandas

\- Geometry operations with Shapely

\- CRS and coordinate transformations with PyProj

\- Geospatial measurement calculations

\- API error handling

\- Automated testing with pytest

\- Git/GitHub based project development



\## Future Scope

Potential improvements include:

\- Persistent database storage for uploaded file metadata

\- Authentication and authorization

\- Asynchronous/background processing for large files

\- Support for additional geospatial formats

\- Support for MultiPolygon and MultiLineString measurements

\- File size and security validation

\- Cloud object storage

\- Spatial database integration such as PostGIS

\- Docker-based deployment

\- Improved API schemas and response validation

\- Frontend map visualization



\## License

This project was developed as a technical assignment for evaluation purposes.





