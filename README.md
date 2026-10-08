# Geospatial File Measurement API

A FastAPI-based REST API for uploading, validating, processing, and measuring geospatial data in **KML** and **Shapefile ZIP** formats.

The API uses **GeoPandas, Shapely, and PyProj** to extract geometries, properties, and Coordinate Reference Systems (CRS), while automatically transforming geographic data to an appropriate projected CRS before calculating accurate **polygon areas** and **LineString lengths**.

---

## ✨ Features

- Upload **KML** files
- Upload **Shapefile ZIP** archives
- Validate required Shapefile components
- Extract geospatial features and properties
- Detect the source **Coordinate Reference System (CRS)**
- Automatically handle geographic CRS for measurements
- Estimate a suitable projected CRS when required
- Calculate:
  - Polygon area
  - LineString length
- Handle Point geometries without measurement
- Gracefully report unsupported geometry types
- Preserve original source geometry in API responses
- RESTful API architecture using FastAPI
- Interactive Swagger/OpenAPI documentation
- Automated testing using `pytest`
- Lightweight in-memory file metadata registry

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python 3.11** | Programming language |
| **FastAPI** | REST API framework |
| **Uvicorn** | ASGI development server |
| **GeoPandas** | Geospatial data processing |
| **Shapely** | Geometry operations |
| **PyProj** | CRS detection and transformation |
| **Pytest** | Automated testing |

---

## 📁 Project Structure

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
│   │   ├── crs_handler.py
│   │   ├── file_processor.py
│   │   └── measurement.py
│   │
│   ├── utils/
│   │   └── validators.py
│   │
│   └── main.py
│
├── tests/
│   ├── test_crs.py
│   ├── test_measurements.py
│   └── test_upload.py
│
├── data/
│   └── .gitkeep
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 🚀 Getting Started

## Prerequisites

Make sure you have the following installed:

- Python **3.11**
- Git
- pip

You can verify your Python version with:

```bash
python --version
```

Expected:

```text
Python 3.11.x
```

---

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/aereo-geospatial-api.git
cd aereo-geospatial-api
```

Replace `<your-username>` with your GitHub username.

---

## 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### Windows Command Prompt

```cmd
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# ▶️ Running the API

Start the development server with:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

---

## 📚 API Documentation

FastAPI automatically provides interactive API documentation.

### Swagger UI

Open:

```text
http://127.0.0.1:8000/docs
```

### ReDoc

Open:

```text
http://127.0.0.1:8000/redoc
```

Swagger UI can be used to upload files and test the API endpoints directly from your browser.

---

# 🔌 API Endpoints

## Upload a File

```http
POST /api/files/
```

Uploads a supported geospatial file.

### Supported formats

- `.kml`
- Shapefile `.zip`

### Shapefile ZIP Requirements

A valid Shapefile archive must contain the following components:

```text
.shp
.shx
.dbf
.prj
```

The API validates these components before attempting to process the geospatial data.

### Example Response

```json
{
  "file_id": "example-file-id",
  "filename": "example.kml",
  "file_type": "kml",
  "status": "uploaded"
}
```

---

# 📄 Get File Metadata

```http
GET /api/files/{file_id}
```

Returns metadata associated with a previously uploaded file.

Example:

```text
GET /api/files/example-file-id
```

---

# 📐 Calculate Measurements

```http
GET /api/files/{file_id}/measurements/
```

Returns information about the processed geospatial features, including:

- Source CRS
- Measurement CRS
- Feature count
- Original feature geometry
- Feature properties
- Geometry type
- Measurement type
- Measurement value
- Measurement unit
- Processing status

---

# 📏 Geometry Measurements

The API determines the measurement operation based on the geometry type.

| Geometry Type | Measurement | Unit |
|---|---|---|
| `Point` | No measurement | — |
| `LineString` | Length | metres |
| `Polygon` | Area | square metres |
| Other | Unsupported | — |

---

## Polygon Example

For a polygon geometry, the API calculates its area.

```json
{
  "geometry_type": "Polygon",
  "measurement_type": "area",
  "value": 12125.53,
  "unit": "square_metres",
  "status": "success"
}
```

---

## LineString Example

For a LineString geometry, the API calculates its length.

```json
{
  "geometry_type": "LineString",
  "measurement_type": "length",
  "value": 155.73,
  "unit": "metres",
  "status": "success"
}
```

---

## Point Example

Point geometries do not have an area or length measurement.

```json
{
  "geometry_type": "Point",
  "measurement_type": null,
  "value": null,
  "unit": null,
  "status": "no_measurement"
}
```

---

# 🌍 CRS Handling

Accurate geospatial measurements should not generally be calculated directly using geographic coordinates such as latitude and longitude.

For example, an uploaded KML file may use:

```text
EPSG:4326
```

EPSG:4326 uses geographic coordinates in degrees. Calculating an area or distance directly from these coordinates would produce values in angular units rather than meaningful metric units.

The API therefore detects the source CRS and prepares a projected CRS for measurement when necessary.

### Processing Concept

```text
Source CRS
   │
   │ EPSG:4326
   ▼
Projected CRS
   │
   │ Suitable metric coordinate system
   ▼
Measurement
   │
   ├── Polygon → Area
   │
   └── LineString → Length
```

For example:

```text
EPSG:4326
    │
    ▼
EPSG:32643
    │
    ▼
Measurement calculation
```

The projected CRS is used internally for measurement calculations.

The original geometry remains available in its **source CRS** in the API response.

---

# 🔄 Processing Flow

```text
                 Upload File
                      │
                      ▼
              Validate File Type
                      │
             ┌────────┴────────┐
             │                 │
            KML          Shapefile ZIP
             │                 │
             │                 ▼
             │         Validate Components
             │         .shp / .shx / .dbf / .prj
             │                 │
             └────────┬────────┘
                      ▼
               Read with GeoPandas
                      │
                      ▼
                Detect Source CRS
                      │
                      ▼
             Prepare Measurement CRS
                      │
                      ▼
             Calculate Measurements
                      │
                      ▼
               Build JSON Response
```

---

# 🏗️ Architecture

The application follows a layered architecture that separates API handling, file processing, CRS operations, and measurement logic.

## API Layer

**Location:**

```text
app/api/routes/files.py
```

Responsibilities:

- Handle file uploads
- Retrieve file metadata
- Trigger measurement processing
- Return API responses
- Handle HTTP-level errors

---

## File Processing Layer

**Location:**

```text
app/services/file_processor.py
```

Responsibilities:

- Read supported geospatial formats
- Process KML files
- Process Shapefile archives
- Extract geometries and properties
- Interface with GeoPandas

---

## CRS Layer

**Location:**

```text
app/services/crs_handler.py
```

Responsibilities:

- Detect source CRS
- Validate CRS information
- Determine whether reprojection is required
- Transform geographic data into a suitable projected CRS

---

## Measurement Layer

**Location:**

```text
app/services/measurement.py
```

Responsibilities:

- Identify geometry types
- Calculate Polygon areas
- Calculate LineString lengths
- Handle Point geometries
- Report unsupported geometries

---

## Validation Layer

**Location:**

```text
app/utils/validators.py
```

Responsibilities:

- Validate uploaded file types
- Validate Shapefile ZIP contents
- Reject invalid archives before geospatial processing

---

## Testing Layer

**Location:**

```text
tests/
```

Contains automated tests covering:

- Measurement calculations
- CRS handling
- File uploads
- Unsupported file types
- Missing files
- API error handling

---

# 🧪 Testing

Run the complete test suite with:

```bash
pytest -q
```

The current test suite covers:

- Point measurement behavior
- LineString length calculation
- Polygon area calculation
- Geographic CRS transformation
- Projected CRS handling
- KML uploads
- Unsupported file rejection
- Missing file handling

---

# 🧠 Design Decisions

## 1. Projected CRS for Measurements

Area and distance calculations are performed using a projected CRS instead of directly using geographic latitude/longitude coordinates.

This avoids treating angular coordinate units as linear units and provides measurements in metric units.

---

## 2. Original Geometry Preservation

The source geometry is preserved for API responses.

Reprojection is performed only for internal measurement calculations.

This allows API consumers to receive geometry in the original CRS while still obtaining measurements in metres or square metres.

---

## 3. Shapefile Validation

A Shapefile is not a single file. It is composed of multiple related files.

The API validates the presence of the essential components:

```text
.shp
.shx
.dbf
.prj
```

Invalid or incomplete Shapefile ZIP archives are rejected before geospatial processing.

---

## 4. In-Memory File Registry

Uploaded file metadata is currently maintained in an in-memory registry.

This keeps the assignment lightweight and avoids introducing unnecessary database infrastructure.

For a production deployment, this could be replaced with persistent storage.

---

# 📊 Example Use Case

A user uploads a KML file containing a polygon representing a land parcel.

```text
KML Upload
    │
    ▼
Detect CRS
    │
    ▼
EPSG:4326
    │
    ▼
Transform to projected CRS
    │
    ▼
Calculate polygon area
    │
    ▼
Return measurement
```

The API can return information such as:

```json
{
  "geometry_type": "Polygon",
  "measurement_type": "area",
  "value": 12125.53,
  "unit": "square_metres",
  "status": "success"
}
```

---

# 🔐 Error Handling

The API handles common invalid input scenarios, including:

- Unsupported file extensions
- Missing files
- Invalid ZIP archives
- Incomplete Shapefile archives
- Missing CRS information
- Unsupported geometry types
- Invalid file identifiers

Errors are returned through appropriate HTTP responses rather than allowing processing failures to propagate as unhandled exceptions.

---

# 📈 Future Improvements

Potential production-level improvements include:

- Persistent database storage for file metadata
- Authentication and authorization
- Asynchronous/background processing for large files
- File size limits and security validation
- Additional geospatial format support
- MultiPolygon measurement support
- MultiLineString measurement support
- Spatial database integration using **PostGIS**
- Cloud object storage
- Docker-based deployment
- Improved request/response schema validation
- Structured logging and monitoring
- Frontend map visualization
- API pagination for large feature collections

---

# 🎯 Learning Outcomes

This project provided practical experience with:

- FastAPI REST API development
- Multipart file uploads
- Geospatial data processing with GeoPandas
- Geometry operations with Shapely
- CRS management and coordinate transformations with PyProj
- Spatial measurement calculations
- API validation and error handling
- Automated testing with Pytest
- Layered backend architecture
- Git and GitHub-based development

---

# 📦 Installation Summary

For quick setup:

```bash
git clone https://github.com/<your-username>/aereo-geospatial-api.git
cd aereo-geospatial-api

python -m venv .venv
```

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

Then:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

Run tests:

```bash
pytest -q
```

---

# 📜 License

This project was developed as a **technical assignment for evaluation purposes**.

---

## 👤 Author

**Liana Salim**

Data Science | AI & Machine Learning | Geospatial Data Processing

GitHub: `https://github.com/Lianasalim`
