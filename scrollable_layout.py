from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy
from PyQt6.QtCore import Qt, QSize

class ScrollableGraphContainer(QScrollArea):
    """A custom scrollable container for graph views that prevents width shrinking"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Setup the scroll area
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create the container widget
        self.container = QWidget()
        self.container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Create the layout for the container
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # Set the container as the scroll area widget
        self.setWidget(self.container)
        
    def add_widget(self, widget):
        """Add a widget to the layout"""
        self.layout.addWidget(widget)
        
        # Force the container to maintain width
        min_width = self.viewport().width() - 30  # Slightly less than viewport to avoid horizontal scrollbar
        self.container.setMinimumWidth(min_width)
        
    def remove_widget(self, widget):
        """Remove a widget from the layout"""
        self.layout.removeWidget(widget)
        widget.deleteLater()
        
    def clear_widgets(self):
        """Clear all widgets from the layout"""
        while self.layout.count() > 0:
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
    def resizeEvent(self, event):
        """Handle resize events to update container width"""
        super().resizeEvent(event)
        
        # Update container width to match viewport width
        min_width = self.viewport().width() - 30
        self.container.setMinimumWidth(min_width)
