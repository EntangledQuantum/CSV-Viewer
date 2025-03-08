from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
                           QPushButton, QLabel, QFileDialog, QSizePolicy, QFrame, QCheckBox)
from PyQt6.QtCore import Qt, QSize

# Update matplotlib backend for PyQt6
import matplotlib
matplotlib.use('QtAgg')  # Using QtAgg backend for PyQt6
import matplotlib.pyplot as plt

# Import matplotlib Qt6 specific backends
try:
    from matplotlib.backends.backend_qt6agg import FigureCanvasQT6Agg as FigureCanvas
    from matplotlib.backends.backend_qt6agg import NavigationToolbar2QT as NavigationToolbar
except ImportError:
    # Fallback to Qt5 backends if Qt6 backends not available
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import pandas as pd
import numpy as np
import re
from scipy import signal, interpolate

# Try to import CSVReader for additional functionality
try:
    from LandMarkCSVReader import CSVReader
    has_csv_reader = True
except ImportError:
    has_csv_reader = False

class GraphView(QFrame):  # Changed to QFrame for better styling
    def __init__(self, data):
        super().__init__()
        self.data = data
        
        # Set up the figure with a fixed size
        self.figure = plt.figure(figsize=(10, 5))
        self.canvas = FigureCanvas(self.figure)
        
        # Ensure the canvas maintains its size
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.canvas.setMinimumHeight(300)
        
        self.initUI()
        
    def initUI(self):
        # Set frame style
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(2)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Controls layout
        control_layout = QHBoxLayout()
        
        # X-axis dropdown
        x_label = QLabel("X-axis:")
        self.x_combo = QComboBox()
        self.x_combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.x_combo.addItems(self.data.columns)
        self.x_combo.currentIndexChanged.connect(self.update_graph)
        
        # Y-axis dropdown
        y_label = QLabel("Y-axis:")
        self.y_combo = QComboBox()
        self.y_combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.y_combo.addItems(self.data.columns)
        
        # Select second column by default for Y-axis if available
        if len(self.data.columns) > 1:
            self.y_combo.setCurrentIndex(1)
            
        self.y_combo.currentIndexChanged.connect(self.update_graph)
        
        # Add checkbox for treating time as numeric
        self.treat_as_numeric_checkbox = QCheckBox("Treat as Numeric")
        self.treat_as_numeric_checkbox.setChecked(True)  # Default to treating as numeric
        self.treat_as_numeric_checkbox.stateChanged.connect(self.update_graph)
        
        # Add checkbox for smoothing the curve
        self.smooth_curve_checkbox = QCheckBox("Smooth Curve")
        self.smooth_curve_checkbox.setChecked(False)  # Disabled by default
        self.smooth_curve_checkbox.stateChanged.connect(self.update_graph)
        
        # Add controls to layout
        control_layout.addWidget(x_label)
        control_layout.addWidget(self.x_combo)
        control_layout.addWidget(y_label)
        control_layout.addWidget(self.y_combo)
        control_layout.addWidget(self.treat_as_numeric_checkbox)
        control_layout.addWidget(self.smooth_curve_checkbox)
        
        # Save button
        save_button = QPushButton("Save Graph")
        save_button.setMaximumWidth(120)
        save_button.clicked.connect(self.save_graph)
        control_layout.addWidget(save_button)
        
        # Remove button
        remove_button = QPushButton("Remove")
        remove_button.setMaximumWidth(120)
        remove_button.clicked.connect(self.remove_graph)
        control_layout.addWidget(remove_button)
        
        # Add stretch to push controls to the left
        control_layout.addStretch()
        
        # Add navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setMaximumHeight(35)
        
        # Add widgets to main layout
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.toolbar)
        main_layout.addWidget(self.canvas)
        
        # Generate initial graph
        self.update_graph()

    def sizeHint(self):
        # Provide a reasonable default size
        return QSize(900, 400)
    
    def minimumSizeHint(self):
        # Provide a minimum size to prevent shrinking too much
        return QSize(800, 350)
    
    def is_likely_time_column(self, col_name):
        """Check if a column is likely to be a time column based on name"""
        time_patterns = ['time', 'timestamp', 'date', 'hour', 'minute', 'second']
        return any(pattern in col_name.lower() for pattern in time_patterns)
        
    def smooth_data(self, x_data, y_data, method='savgol'):
        """Smooth data using either Savitzky-Golay filter or cubic spline interpolation"""
        # Make sure we're working with numeric data
        x_data_numeric = pd.to_numeric(x_data, errors='coerce').dropna().to_numpy()
        y_data_numeric = pd.to_numeric(y_data, errors='coerce').dropna().to_numpy()
        
        # Make sure we have enough data points for smoothing
        if len(x_data_numeric) < 5 or len(y_data_numeric) < 5:
            return x_data, y_data  # Return original data if not enough points
        
        # Get only finite values
        valid_indices = np.isfinite(x_data_numeric) & np.isfinite(y_data_numeric)
        x_valid = x_data_numeric[valid_indices]
        y_valid = y_data_numeric[valid_indices]
        
        # Sort by x values (important for interpolation)
        sort_indices = np.argsort(x_valid)
        x_sorted = x_valid[sort_indices]
        y_sorted = y_valid[sort_indices]
        
        try:
            if method == 'savgol':
                # Savitzky-Golay filter (good for noisy data)
                # Window size must be odd and less than data length
                window_length = min(11, len(y_sorted) - (len(y_sorted) % 2) - 1)
                if window_length > 2:  # Need at least window_length > polyorder
                    y_smooth = signal.savgol_filter(y_sorted, window_length, 3)
                    return x_sorted, y_smooth
            else:
                # Cubic spline interpolation (smooth curve through points)
                # Create more points for a smoother curve
                x_new = np.linspace(min(x_sorted), max(x_sorted), num=min(1000, len(x_sorted)*5))
                # Create the interpolation function
                spline = interpolate.interp1d(x_sorted, y_sorted, kind='cubic', bounds_error=False)
                # Apply the interpolation function to the new x points
                y_new = spline(x_new)
                return x_new, y_new
        except Exception as e:
            print(f"Error smoothing data: {e}")
            
        # Return original data if smoothing fails
        return x_data, y_data
        
    def update_graph(self):
        # Clear the figure
        self.figure.clear()
        
        try:
            # Get selected columns
            x_col = self.x_combo.currentText()
            y_col = self.y_combo.currentText()
            
            # Create plot
            ax = self.figure.add_subplot(111)
            
            # Get data for plotting
            x_data = self.data[x_col]
            y_data = self.data[y_col]
            
            # Check if we should try to parse as datetime
            parse_as_datetime = False
            
            # Only parse as datetime if the checkbox is unchecked and column name suggests time/date
            if not self.treat_as_numeric_checkbox.isChecked():
                if has_csv_reader and x_col in CSVReader.detect_datetime_columns(self.data):
                    parse_as_datetime = True
                else:
                    # Try to detect if this is a datetime column
                    try:
                        if self.is_likely_time_column(x_col):
                            test_parse = pd.to_datetime(self.data[x_col])
                            parse_as_datetime = True
                    except:
                        parse_as_datetime = False
            
            # Parse as datetime if needed
            is_datetime = False
            if parse_as_datetime:
                try:
                    x_data = pd.to_datetime(self.data[x_col])
                    is_datetime = True
                except:
                    pass
            
            # Apply smoothing if checkbox is checked
            if self.smooth_curve_checkbox.isChecked():
                try:
                    # For datetime, convert to numeric timestamps first
                    if is_datetime:
                        x_numeric = x_data.astype(np.int64) // 10**9  # Convert to Unix timestamp
                        x_smooth, y_smooth = self.smooth_data(x_numeric, y_data)
                        # Plot original data as points
                        ax.scatter(x_data, y_data, s=15, alpha=0.5, label='Original Data')
                        # Plot smoothed data as line
                        if isinstance(x_smooth[0], (int, float)):
                            # Convert back to datetime for plotting
                            x_smooth_dt = pd.to_datetime(x_smooth, unit='s')
                            ax.plot(x_smooth_dt, y_smooth, '-', lw=2, label='Smoothed')
                        else:
                            ax.plot(x_data, y_smooth, '-', lw=2, label='Smoothed')
                        ax.legend()
                    else:
                        # For regular numeric data
                        x_smooth, y_smooth = self.smooth_data(x_data, y_data)
                        # Plot original data as points
                        ax.scatter(x_data, y_data, s=15, alpha=0.5, label='Original Data')
                        # Plot smoothed data as line
                        ax.plot(x_smooth, y_smooth, '-', lw=2, label='Smoothed')
                        ax.legend()
                except Exception as e:
                    print(f"Error applying smoothing: {e}")
                    # Fall back to regular plotting if smoothing fails
                    ax.plot(x_data, y_data, '-o', markersize=4)
            else:
                # Regular plotting without smoothing
                ax.plot(x_data, y_data, '-o', markersize=4)
            
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.set_title(f"{y_col} vs {x_col}")
            
            if is_datetime:
                self.figure.autofmt_xdate()
            
            # Add grid
            ax.grid(True, linestyle='--', alpha=0.7)
            
            # Show the plot
            self.canvas.draw()
            
        except Exception as e:
            print(f"Error updating graph: {str(e)}")
    
    def save_graph(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Graph", "", 
                                                 "PNG (*.png);;JPEG (*.jpg);;PDF (*.pdf);;SVG (*.svg)")
        if file_path:
            self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
    
    def remove_graph(self):
        # Remove this widget from parent layout
        parent = self.parent()
        parent.layout().removeWidget(self)
        self.deleteLater()