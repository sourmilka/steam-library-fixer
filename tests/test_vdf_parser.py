"""
Basic tests for Steam Library Fixer
"""

import pytest
from pathlib import Path
from src.vdf_parser import VDFParser


def test_vdf_parser_simple():
    """Test parsing simple VDF content."""
    content = '''
    "TestKey"
    {
        "name"  "TestValue"
        "number"    "42"
    }
    '''
    
    result = VDFParser.parse(content)
    assert 'TestKey' in result
    assert result['TestKey']['name'] == 'TestValue'
    assert result['TestKey']['number'] == 42


def test_vdf_parser_nested():
    """Test parsing nested VDF structure."""
    content = '''
    "Root"
    {
        "Level1"
        {
            "Level2"
            {
                "value" "deep"
            }
        }
    }
    '''
    
    result = VDFParser.parse(content)
    assert result['Root']['Level1']['Level2']['value'] == 'deep'


def test_vdf_write():
    """Test writing VDF format."""
    data = {
        'AppState': {
            'name': 'Test Game',
            'appid': '12345',
            'StagingFolder': '0'
        }
    }
    
    output = VDFParser.write(data)
    assert '"AppState"' in output
    assert '"name"' in output
    assert '"Test Game"' in output


if __name__ == '__main__':
    pytest.main([__file__])
