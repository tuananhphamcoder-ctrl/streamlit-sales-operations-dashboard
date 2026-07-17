# Streamlit Sales & Operations Dashboard

An interactive Streamlit application for validating factory operations data,
analyzing production and workforce KPIs, applying business filters, and
downloading cleaned data and Excel reports.

## Business problem

Production and operations teams often receive Excel or CSV files that require
manual validation before managers can review performance. Invalid dates,
incorrect numeric values, duplicate rows, and inconsistent operational values
can make reports unreliable.

## Solution

The application:

- Uploads CSV, XLSX, or XLS files
- Validates required columns
- Detects exact duplicates
- Identifies invalid dates and numeric values
- Checks operational business rules
- Calculates production and workforce KPIs
- Filters by date, production line, process, and shift
- Displays interactive Plotly charts
- Downloads cleaned data and KPI reports

## Synthetic data

- Clean source rows: **2,190**
- Messy source rows: **2,212**
- Production lines: **3**
- Shifts: **2**
- Reporting year: **2025**

All data is synthetic. No real company, employee, or production information is
included.

## KPIs

- Plan attainment
- Defect rate
- Availability
- Output per employee
- Overtime rate
- Absence rate
- Planned output
- Actual output
- Production gap

## Project structure

```text
streamlit-sales-operations-dashboard/
├── app.py
├── data/
│   ├── sample_factory_operations.csv
│   ├── sample_factory_operations.xlsx
│   ├── messy_factory_operations.csv
│   ├── messy_factory_operations.xlsx
│   └── reference/
├── src/
│   ├── config.py
│   ├── data_loader.py
│   ├── validators.py
│   ├── metrics.py
│   ├── charts.py
│   └── exporters.py
├── tests/
├── screenshots/
├── requirements.txt
└── README.md
```

## Run locally

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest
python -m streamlit run app.py
```

## Deploy

Deploy the repository on Streamlit Community Cloud using:

```text
Main file path: app.py
Branch: main
```

## Portfolio positioning

This project extends the operations KPI reporting automation into a live,
interactive dashboard that a client can test directly in a browser.
