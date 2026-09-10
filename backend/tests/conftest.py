import os
import sys
from dotenv import load_dotenv

# Ensure tests/ is on sys.path so `from conftest import ...` works when
# pytest is invoked from /app/backend (tests/ is a package with __init__.py).
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

TEST_USER_PASSWORD = os.environ.get("TEST_USER_PASSWORD", "")
