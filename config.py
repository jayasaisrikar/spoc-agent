"""
Configuration and package initialization for AI Code Architecture Agent
"""
import os
import sys

# Add src directory to Python path for proper imports
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')

if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Version information
__version__ = "1.0.0"
__author__ = "Jayasai Srikar"
__email__ = "jayasaisrikar@example.com"

# Project paths
PROJECT_ROOT = project_root
SRC_PATH = src_path
STATIC_PATH = os.path.join(project_root, 'static')
CACHE_PATH = os.path.join(project_root, 'cache')
