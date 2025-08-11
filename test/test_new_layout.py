#!/usr/bin/env python3

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QFrame, QLabel
from PyQt5.QtCore import Qt
from src.clock_widget import TimeOnlyWidget, DateOnlyWidget
from src.mallard_svg_widget import MallardSVGWidget

def test_new_layout():
    """Test the new layout with MALLARD in top right and time next to date"""
    app = QApplication(sys.argv)
    
    # Create a test window
    window = QMainWindow()
    window.setWindowTitle("New Layout Test")
    window.showFullScreen()
    window.setStyleSheet("background-color: #000000;")
    
    # Create central widget
    central_widget = QWidget()
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    
    # Top section: Navigation (centered)
    nav_label = QLabel("Navigation Bar")
    nav_label.setStyleSheet("color: #00FFA3; font-size: 16px; padding: 10px;")
    nav_label.setAlignment(Qt.AlignCenter)
    main_layout.addWidget(nav_label)
    
    # Date and Time section
    date_container = QFrame()
    date_layout = QHBoxLayout(date_container)
    date_layout.setContentsMargins(0, 5, 0, 5)
    
    # Date widget
    date_widget = DateOnlyWidget()
    date_widget.setFixedHeight(25)
    
    # Time widget
    time_widget = TimeOnlyWidget()
    time_widget.setFixedHeight(25)
    
    date_layout.addStretch(1)
    date_layout.addWidget(date_widget)
    date_layout.addSpacing(20)  # Space between date and time
    date_layout.addWidget(time_widget)
    date_layout.addStretch(1)
    
    main_layout.addWidget(date_container)
    
    # Content area (simulated)
    content_label = QLabel("Content Area\n(YouTube, Maps, etc.)")
    content_label.setStyleSheet("color: #666; font-size: 24px; padding: 50px;")
    content_label.setAlignment(Qt.AlignCenter)
    main_layout.addWidget(content_label, 1)  # Stretch
    
    window.setCentralWidget(central_widget)
    window.show()
    
    print("New layout test running...")
    print("You should see:")
    print("1. Navigation bar centered at top")
    print("2. Date and time centered below navbar (same font style/size)")
    print("3. Content area taking remaining space")
    print("4. All elements visible in fullscreen")
    
    return app.exec()

if __name__ == "__main__":
    print("Testing new layout...")
    sys.exit(test_new_layout()) 
