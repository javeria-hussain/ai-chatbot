import sys
import os

# App directory ko python path mein add karne ke liye
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.main import app
