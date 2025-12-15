"""
Test utilities
"""

import pytest
from src.utils import format_bytes, get_app_id_from_filename


def test_format_bytes():
    """Test byte formatting."""
    assert format_bytes(1024) == "1.00 KB"
    assert format_bytes(1048576) == "1.00 MB"
    assert format_bytes(1073741824) == "1.00 GB"


def test_get_app_id_from_filename():
    """Test extracting app ID from manifest filename."""
    assert get_app_id_from_filename("appmanifest_3564740.acf") == "3564740"
    assert get_app_id_from_filename("appmanifest_123.acf") == "123"
    assert get_app_id_from_filename("invalid.acf") is None


if __name__ == '__main__':
    pytest.main([__file__])
