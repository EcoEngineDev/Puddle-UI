#!/usr/bin/env python3

# Test script to verify widget configuration
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.widget_config import WIDGET_WIDTH, WIDGET_HEIGHT, MINIMAP_SIZE

print("=== Widget Size Configuration Test ===")
print(f"Widget Width: {WIDGET_WIDTH}px")
print(f"Widget Height: {WIDGET_HEIGHT}px")
print(f"Minimap Size: {MINIMAP_SIZE}x{MINIMAP_SIZE}px")
print(f"Widget Area: {WIDGET_WIDTH * WIDGET_HEIGHT} square pixels")
print("=====================================")

# Test different configurations
print("\n=== Common Size Examples ===")
sizes = [
    (1280, 300, "Compact"),
    (1280, 768, "Standard"),
    (1600, 900, "Full HD"),
    (1920, 1080, "1080p"),
    (2560, 1440, "2K"),
    (3840, 2160, "4K")
]

for width, height, name in sizes:
    area = width * height
    print(f"{name}: {width}x{height} = {area:,} pixels")

print("\nTo change widget sizes, edit widget_config.py and change:")
print("WIDGET_WIDTH = 1280")
print("WIDGET_HEIGHT = 300")
print("MINIMAP_SIZE = 300") 
