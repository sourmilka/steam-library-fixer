"""
Steam Library Fixer - VDF Parser Module
Parses and writes Valve Data Format (VDF) files used by Steam.
"""

import re
from typing import Any, Dict, Union
from pathlib import Path


class VDFParser:
    """Parser for Valve Data Format files (.vdf and .acf)."""
    
    @staticmethod
    def parse(content: str) -> Dict[str, Any]:
        """
        Parse VDF content into a Python dictionary.
        
        Args:
            content: Raw VDF file content
            
        Returns:
            Dict: Parsed VDF data
        """
        lines = content.split('\n')
        return VDFParser._parse_section(lines, 0)[0]
    
    @staticmethod
    def _parse_section(lines: list, start_idx: int) -> tuple:
        """
        Recursively parse a VDF section.
        
        Args:
            lines: List of file lines
            start_idx: Starting line index
            
        Returns:
            tuple: (parsed_dict, end_index)
        """
        result = {}
        i = start_idx
        current_key = None
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('//'):
                i += 1
                continue
            
            # End of section
            if line == '}':
                return result, i + 1
            
            # Parse key-value pairs
            tokens = VDFParser._tokenize(line)
            
            if len(tokens) >= 1:
                if tokens[0] == '{':
                    # Start of nested section for current key
                    if current_key:
                        nested_data, new_idx = VDFParser._parse_section(lines, i + 1)
                        result[current_key] = nested_data
                        i = new_idx
                        current_key = None
                    else:
                        i += 1
                elif len(tokens) == 1:
                    # Key without value (next line will be {)
                    current_key = tokens[0]
                    i += 1
                elif len(tokens) == 2:
                    # Key-value pair
                    key, value = tokens
                    # Try to convert numeric values
                    try:
                        if '.' in value:
                            value = float(value)
                        else:
                            value = int(value)
                    except ValueError:
                        pass  # Keep as string
                    result[key] = value
                    i += 1
                else:
                    i += 1
            else:
                i += 1
        
        return result, i
    
    @staticmethod
    def _tokenize(line: str) -> list:
        """
        Extract tokens from a VDF line.
        
        Args:
            line: Single line from VDF file
            
        Returns:
            list: List of tokens (strings)
        """
        tokens = []
        # Match quoted strings and unquoted tokens
        pattern = r'"([^"]*)"|(\S+)'
        matches = re.findall(pattern, line)
        
        for match in matches:
            # match is a tuple (quoted_content, unquoted_content)
            token = match[0] if match[0] else match[1]
            if token:
                tokens.append(token)
        
        return tokens
    
    @staticmethod
    def write(data: Dict[str, Any], indent_level: int = 0) -> str:
        """
        Convert Python dictionary back to VDF format.
        
        Args:
            data: Dictionary to convert
            indent_level: Current indentation level
            
        Returns:
            str: VDF formatted string
        """
        lines = []
        indent = '\t' * indent_level
        
        for key, value in data.items():
            if isinstance(value, dict):
                # Nested section
                lines.append(f'{indent}"{key}"')
                lines.append(f'{indent}{{')
                lines.append(VDFParser.write(value, indent_level + 1))
                lines.append(f'{indent}}}')
            else:
                # Key-value pair
                lines.append(f'{indent}"{key}"\t\t"{value}"')
        
        return '\n'.join(lines)
    
    @staticmethod
    def read_file(file_path: Path) -> Dict[str, Any]:
        """
        Read and parse a VDF file.
        
        Args:
            file_path: Path to VDF file
            
        Returns:
            Dict: Parsed VDF data
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return VDFParser.parse(content)
    
    @staticmethod
    def write_file(data: Dict[str, Any], file_path: Path) -> bool:
        """
        Write dictionary to VDF file.
        
        Args:
            data: Dictionary to write
            file_path: Output file path
            
        Returns:
            bool: True if successful
        """
        try:
            content = VDFParser.write(data)
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                f.write(content)
            return True
        except Exception:
            return False


def read_manifest(manifest_path: Path) -> Dict[str, Any]:
    """
    Read a Steam app manifest file (.acf).
    
    Args:
        manifest_path: Path to manifest file
        
    Returns:
        Dict: Parsed manifest data
    """
    return VDFParser.read_file(manifest_path)


def write_manifest(data: Dict[str, Any], manifest_path: Path) -> bool:
    """
    Write manifest data to file.
    
    Args:
        data: Manifest dictionary
        manifest_path: Output path
        
    Returns:
        bool: True if successful
    """
    return VDFParser.write_file(data, manifest_path)


def read_library_folders(vdf_path: Path) -> Dict[str, Any]:
    """
    Read libraryfolders.vdf file.
    
    Args:
        vdf_path: Path to libraryfolders.vdf
        
    Returns:
        Dict: Parsed library folders data
    """
    return VDFParser.read_file(vdf_path)


def write_library_folders(data: Dict[str, Any], vdf_path: Path) -> bool:
    """
    Write library folders data to file.
    
    Args:
        data: Library folders dictionary
        vdf_path: Output path
        
    Returns:
        bool: True if successful
    """
    return VDFParser.write_file(data, vdf_path)
