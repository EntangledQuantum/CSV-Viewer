# Landmark CSV Viewer

A Python application for visualizing CSV data with customizable graphs.

## Features

- Load CSV files with at least 2 columns
- Create multiple graph views
- Select different columns for X and Y axes
- Auto-detects datetime columns
- Save graphs as PNG, JPEG, PDF, or SVG
- Interactive matplotlib toolbar for zooming, panning, etc.

## Installation

1. Install the required packages:
```
pip install -r requirements.txt
```

## Running the Application

You can run the application using:

```
python LandMarkCSVReader.py
```

Or

```
python run.py
```
![Screenshot 2025-03-07 001438](https://github.com/user-attachments/assets/1873c2e9-e81a-47f4-85d9-568b44ee2e2c)

## Usage

1. Click "Open CSV" to load a CSV file
2. The application will automatically create an initial graph
3. Use the dropdowns to select X and Y axis data
4. Add additional graphs with the "Add Graph" button
5. Save any graph using the "Save Graph" button

## Requirements

- Python 3.6+
- PyQt6
- Matplotlib
- Pandas



