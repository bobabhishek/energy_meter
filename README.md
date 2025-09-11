# Energy Meter Reading System

A simple Flask app to extract energy meter readings from uploaded images using OpenCV and Tesseract OCR, store readings with metadata, and compute consumption over time.

## Project Structure
```
energy_meter/
├── static/
│   └── uploads/
├── templates/
│   └── index.html
├── data/
│   └── readings.csv
├── app.py
├── meter_reader.py
├── data_handler.py
├── requirements.txt
└── README.md
```

## Setup

1) Create and activate a virtual environment (recommended)
```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
```

2) Install dependencies
```powershell
pip install -r requirements.txt
```

3) Install Tesseract OCR
- Windows: see `https://github.com/UB-Mannheim/tesseract/wiki`
- Linux: `sudo apt-get install tesseract-ocr`

4) (Optional) Set Tesseract path via environment variable if not in default location
```powershell
$env:TESSERACT_CMD = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
```

5) Create required folders (already created on first run)
```powershell
mkdir -Force static\uploads, data
```

## Run
```powershell
python app.py
```
Open `http://localhost:5000` in your browser.

## Web App Usage (POC)
- Upload a meter display image (JPG/PNG). The app extracts the kWh reading, stores it with timestamp and simulated geolocation, and shows the result.
- In Consumption Analysis, choose a period (daily/weekly/monthly) and optionally select a start/end date to filter the calculation. Results are shown as JSON (first/last reading and computed consumption per bucket).

## Approach
- OCR via Tesseract with OpenCV preprocessing:
  - Grayscale + CLAHE contrast enhancement
  - Adaptive thresholding + median blur + light dilation
  - Multiple OCR configs tried (`--psm 7/6/8`) with digit/decimal whitelist
  - Post-processing normalizes common OCR confusions (O→0, S→5, comma→dot) and parses the first plausible number
- Metadata: timestamp via system time; geolocation simulated within Bangalore bounds.
- Storage: CSV (`data/readings.csv`).
- Consumption: resample by day/week/month; compute delta between first/last reading in each period; optional start/end date filter.

## Assumptions
- Meter displays numeric kWh, optionally with decimals.
- Images are reasonably cropped or with digits clearly visible.
- Tesseract is installed and accessible (Windows default path or `TESSERACT_CMD`).
- Readings are monotonically non-decreasing; consumption is last-first in period.

## Example Demo Steps
1. Ensure Tesseract installed and environment configured as needed.
2. Run the app and open the web UI.
3. Upload 3–5 sample meter images (in chronological order).
4. Verify readings and metadata appear.
5. Choose period Daily; click Calculate to see consumption.
6. Add a start date (e.g., first reading date) and end date (e.g., last reading date) and recalc.
7. Take screenshots of upload result and consumption JSON for documentation.

## Notes
- OCR accuracy depends on image quality and meter type.
- Geolocation is simulated around Bangalore.
- Data stored as CSV for simplicity.
- Consumption assumes chronological readings.
- Production hardening (auth, validation, better preprocessing) is out of scope.
