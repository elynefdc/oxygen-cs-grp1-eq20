"""import pytest
from dotenv import load_dotenv
import os
from src.main import Main

load_dotenv()

# Tests
def test_environment_variables():
    
    assert os.environ.get("T_MAX")  <= "100"
    assert os.environ.get("T_MIN")  >= "0"
    assert os.environ.get("T_MIN") < os.environ.get("T_MAX")
    
"""
