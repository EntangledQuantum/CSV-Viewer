import sys
import os
import pandas as pd
from PyQt6.QtWidgets import (QApplication, QMainWindow, QFileDialog, QVBoxLayout, 
                           QHBoxLayout, QWidget, QPushButton, QMessageBox, QLabel)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QSizePolicy
from graph_view import GraphView
from scrollable_layout import ScrollableGraphContainer

# Import CSVReader if it exists in the same module, otherwise create a backup import plan
try:
    from LandMarkCSVReader import CSVReader
except ImportError:
    CSVReader = None

class CSVViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.csv_data = None
        self.graph_views = []
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('CSV Graph Viewer')
        self.setGeometry(100, 100, 1200, 800)  # Larger initial window size
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Open CSV button
        open_btn = QPushButton('Open CSV', self)
        open_btn.clicked.connect(self.open_csv)
        button_layout.addWidget(open_btn)
        
        # Add Graph button
        self.add_graph_btn = QPushButton('Add Graph', self)
        self.add_graph_btn.clicked.connect(self.add_graph_view)
        self.add_graph_btn.setEnabled(False)
        button_layout.addWidget(self.add_graph_btn)
        
        # Add spacer to push buttons to the left
        button_layout.addStretch()
        
        # Add button layout to main layout
        main_layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel("Please open a CSV file to start.")
        main_layout.addWidget(self.status_label)
        
        # Use our custom ScrollableGraphContainer
        self.scroll_container = ScrollableGraphContainer()
        main_layout.addWidget(self.scroll_container)
        
        self.setCentralWidget(main_widget)
        
    def open_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)")
        if file_path:
            try:
                # Use CSVReader if available, otherwise fall back to pandas directly
                if CSVReader:
                    self.csv_data = CSVReader.read_csv(file_path, self)
                    if self.csv_data is None:
                        return
                else:
                    # Read the CSV file
                    self.csv_data = pd.read_csv(file_path)
                    
                    # Check if there are at least 2 columns
                    if len(self.csv_data.columns) < 2:
                        QMessageBox.critical(self, "Error", "CSV must have at least 2 columns.")
                        self.csv_data = None
                        return
                
                # Enable add graph button and clear any existing graphs
                self.add_graph_btn.setEnabled(True)
                self.clear_graphs()
                
                # Add an initial graph
                self.add_graph_view()
                
                # Update status
                self.status_label.setText(f"Loaded: {os.path.basename(file_path)} with {len(self.csv_data)} rows and {len(self.csv_data.columns)} columns")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open CSV file: {str(e)}")
    
    def add_graph_view(self):
        if self.csv_data is not None:
            # Create new graph view
            graph_view = GraphView(self.csv_data)
            
            # Add to custom scrollable container
            self.scroll_container.add_widget(graph_view)
            self.graph_views.append(graph_view)
    
    def clear_graphs(self):
        # Use our custom clear method
        self.scroll_container.clear_widgets()
        self.graph_views = []

def main():
    app = QApplication(sys.argv)
    
    # Set application style for better appearance
    app.setStyle("Fusion")
    
    viewer = CSVViewer()
    viewer.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
