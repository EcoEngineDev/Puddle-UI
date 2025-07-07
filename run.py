#!/usr/bin/env python3
"""
MALLARD Car Interface - Startup Script
This script handles the startup and dependency checks for the car interface.
"""

import sys
import os
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import PyQt5
        print("✓ PyQt5 is available")
        return True
    except ImportError:
        print("✗ PyQt5 is not installed")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def main():
    """Main startup function"""
    print("🚗 Starting MALLARD Car Interface...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if icon files exist
    icon_dir = "Media/Icons"
    if not os.path.exists(icon_dir):
        print(f"⚠️  Warning: Icon directory '{icon_dir}' not found")
        print("Some icons may not display properly")
    
    # Import and run the main application
    try:
        import main
        print("✓ Starting interface...")
    except Exception as e:
        print(f"✗ Error starting interface: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 