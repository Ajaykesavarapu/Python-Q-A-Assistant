import os
import sys

# 1. Resolve absolute path of backend directories
backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "python-qa-assistant"))
backend_app_path = os.path.abspath(os.path.join(backend_root, "app"))

# 2. Change current working directory to backend root
# This makes sure that relative paths like './chroma_db' resolve correctly in backend code
os.chdir(backend_root)

# 3. Add backend root to sys.path so Python can resolve imports cleanly
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

# 4. Extend __path__ so that Python imports like 'app.main' and 'app.api' 
# are correctly resolved from the backend 'app/' directory.
__path__.append(backend_app_path)
