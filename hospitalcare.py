#!/usr/bin/env python
"""
hospitalcare — Top-level entry point script.

Usage:
  python hospitalcare.py [COMMAND] [OPTIONS]
  
Or install via `pip install -e .` and run `hospitalcare [COMMAND]`.
"""
import sys
import os

# Make sure the project root is on the path so `cli` package can be found
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from cli.main import app

if __name__ == "__main__":
    app()
