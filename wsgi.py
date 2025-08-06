#!/usr/bin/env python3
"""
WSGI entry point for PythonAnywhere deployment
Arusha Catholic Seminary School Management System
"""

import sys
import os

# Add the backend directory to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

# Import the FastAPI app from server.py
from server import app

# For PythonAnywhere, we need to use the ASGI application directly
# PythonAnywhere supports ASGI applications natively
application = app
