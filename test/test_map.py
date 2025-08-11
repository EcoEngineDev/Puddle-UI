import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from src.web_embed.maps import MapsWidget

# Load environment variables from .env file
load_dotenv()

# Debug: Check if API key is loaded
api_key = os.getenv("GOOGLE_MAPS_API_KEY")
if api_key:
    print(f"✅ Google Maps API key loaded successfully (length: {len(api_key)})")
else:
    print("❌ Google Maps API key not found in environment variables")
    print("   Make sure your .env file contains: GOOGLE_MAPS_API_KEY=your_actual_key")

class TestMapWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Maps Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create and add the map widget
        print("Creating MapsWidget...")
        self.map_widget = MapsWidget()
        layout.addWidget(self.map_widget)
        
        print("Map widget created successfully!")
        print("If you see a map loading, your API key is working correctly.")
        print("If you see an error or blank screen, check your API key.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create and show the test window
    window = TestMapWindow()
    window.show()
    
    print("Test window opened. Check the map to see if your API key is working.")
    
    sys.exit(app.exec_()) 
