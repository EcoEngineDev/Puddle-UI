#!/usr/bin/env python3

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout
from clock_widget import TimeOnlyWidget, DateOnlyWidget
from mallard_svg_widget import MallardSVGWidget

def test_time_display():
    """Test the time display and MALLARD SVG in isolation"""
    app = QApplication(sys.argv)
    
    # Create a test window
    window = QMainWindow()
    window.setWindowTitle("Time Display Test")
    window.resize(800, 400)
    window.setStyleSheet("background-color: #000000;")
    
    # Create central widget
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    layout.setContentsMargins(20, 20, 20, 20)
    
    # Create date widget (top)
    date_widget = DateOnlyWidget()
    layout.addWidget(date_widget)
    
    # Add some spacing
    layout.addStretch(1)
    
    # Create time widget (center)
    time_widget = TimeOnlyWidget()
    layout.addWidget(time_widget)
    
    # Create MALLARD SVG widget (bottom)
    mallard_widget = MallardSVGWidget()
    layout.addWidget(mallard_widget)
    
    window.setCentralWidget(central_widget)
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    print("Testing time display and MALLARD SVG...")
    print("You should see:")
    print("1. Date at the top (e.g., 'AUG 2')")
    print("2. Time in the center (e.g., '14:30') updating every second")
    print("3. MALLARD SVG at the bottom")
    sys.exit(test_time_display()) 