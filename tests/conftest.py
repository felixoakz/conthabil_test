import sys
import os

"""
Add the project root to the Python path to allow imports from 'main' and 'src'.
"""

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
