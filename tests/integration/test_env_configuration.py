"""
Integration Test
"""

from pathlib import Path


def test_env_example_exists():

    assert Path(".env.example").exists()
