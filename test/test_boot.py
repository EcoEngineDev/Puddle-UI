#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from PyQt5.QtWidgets import QApplication
from src.boot_animation import BootAnimation

def test_boot_animation():
    """Test the boot animation in isolation"""
    app = QApplication(sys.argv)
    
    # Create a test window
    from PyQt5.QtWidgets import QMainWindow
    window = QMainWindow()
    window.setWindowTitle("Boot Animation Test")
    window.resize(800, 600)
    window.show()
    
    # Create boot animation
    boot_anim = BootAnimation(window)
    boot_anim.resize(800, 600)
    
    # Connect signal
    boot_anim.boot_complete.connect(lambda: print("Boot animation complete!"))
    
    # Start boot sequence
    boot_anim.start_boot_sequence()
    
    return app.exec()

if __name__ == "__main__":
    print("Testing boot animation...")
    print("Make sure Media/boot.png and Media/SFX/boot.wav exist")
    
    # Check if files exist
    boot_image = os.path.join("Media", "boot.png")
    boot_sound = os.path.join("Media", "SFX", "boot.wav")
    
    if not os.path.exists(boot_image):
        print(f"Warning: Boot image not found at {boot_image}")
    else:
        print(f"✓ Boot image found: {boot_image}")
        
    if not os.path.exists(boot_sound):
        print(f"Warning: Boot sound not found at {boot_sound}")
    else:
        print(f"✓ Boot sound found: {boot_sound}")
    
    sys.exit(test_boot_animation()) 
