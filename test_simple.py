#!/usr/bin/env python3

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class SimpleTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Test")
        self.setGeometry(100, 100, 400, 300)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create label
        label = QLabel("Test Label - If you can see this, PyQt5 is working!")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        print("Simple test window created successfully!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleTest()
    window.show()
    print("Application started successfully!")
    sys.exit(app.exec_()) 