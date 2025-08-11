#!/usr/bin/env python3

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from src.clock_widget import ClockWidget

def test_clock_widget():
    """Test the clock widget in isolation"""
    app = QApplication(sys.argv)
    
    # Create a test window
    window = QMainWindow()
    window.setWindowTitle("Clock Widget Test")
    window.resize(400, 300)
    
    # Create central widget
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Create clock widget
    clock = ClockWidget()
    layout.addWidget(clock)
    
    # Add some spacing
    layout.addStretch(1)
    
    window.setCentralWidget(central_widget)
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    print("Testing clock widget...")
    print("You should see the current time and date updating every second")
    sys.exit(test_clock_widget()) 
