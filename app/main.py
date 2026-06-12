import os
import sys

# 1. Resolve absolute path of python-qa-assistant subdirectory
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "python-qa-assistant"))

# 2. Change current working directory to python-qa-assistant
# This makes sure that relative paths like './chroma_db' or './data' resolve correctly
os.chdir(backend_path)

# 3. Insert backend path to sys.path so Python can find the real app package
sys.path.insert(0, backend_path)

# 4. Remove root-level 'app' module from sys.modules to prevent circular imports
if "app" in sys.modules:
    del sys.modules["app"]

# 5. Import the real FastAPI app instance
from app.main import app as real_app

# Expose it globally for Uvicorn
app = real_app
