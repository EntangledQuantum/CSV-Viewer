import sys
import pandas as pd
from PyQt6.QtWidgets import QApplication, QMessageBox
from csv_viewer import CSVViewer

class CSVReader:
    """A class for reading and validating CSV files specifically for landmark data"""
    
    @staticmethod
    def read_csv(file_path, parent_widget=None):
        """
        Read a CSV file and validate it
        
        Args:
            file_path (str): Path to the CSV file
            parent_widget: Parent widget for showing error dialogs
            
        Returns:
            pandas.DataFrame or None: The CSV data if valid, None otherwise
        """
        try:
            # Read the CSV file
            data = pd.read_csv(file_path)
            
            # Validate the CSV file
            if len(data.columns) < 2:
                if parent_widget:
                    QMessageBox.critical(parent_widget, "Error", "CSV must have at least 2 columns.")
                return None
                
            return data
            
        except Exception as e:
            if parent_widget:
                QMessageBox.critical(parent_widget, "Error", f"Failed to open CSV file: {str(e)}")
            return None
    
    @staticmethod
    def detect_datetime_columns(data):
        """
        Detect columns that may contain datetime values
        
        Args:
            data (pandas.DataFrame): The CSV data
            
        Returns:
            list: List of column names that likely contain datetime values
        """
        datetime_columns = []
        
        for col in data.columns:
            try:
                # Try to convert to datetime
                pd.to_datetime(data[col])
                datetime_columns.append(col)
            except:
                pass
                
        return datetime_columns
    
    @staticmethod
    def get_numeric_columns(data):
        """
        Get columns that contain numeric values
        
        Args:
            data (pandas.DataFrame): The CSV data
            
        Returns:
            list: List of column names that contain numeric values
        """
        return data.select_dtypes(include=['number']).columns.tolist()


def main():
    """Launch the CSV Viewer application"""
    app = QApplication(sys.argv)
    app.setApplicationName("Landmark CSV Viewer")
    viewer = CSVViewer()
    viewer.setWindowTitle("Landmark CSV Viewer")
    viewer.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
