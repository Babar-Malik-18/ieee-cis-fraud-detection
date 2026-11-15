"""
backend/test_api.py
Direct executable API test script.
"""

from tests.test_api import *

if __name__ == "__main__":
    import pytest
    pytest.main(["-v", "backend/tests/test_api.py"])
