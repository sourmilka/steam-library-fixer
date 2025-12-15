#!/usr/bin/env python3
"""
Setup script for Steam Library Fixer
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="steam-library-fixer",
    version="1.0.0",
    author="Steam Library Fixer Contributors",
    description="Automatic Steam library repair tool for fixing configuration issues",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/steam-library-fixer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "colorama>=0.4.6",
        "rich>=13.7.0",
        "psutil>=5.9.8",
        "click>=8.1.7",
    ],
    entry_points={
        'console_scripts': [
            'steam-fixer=src.main:main',
        ],
    },
    keywords=[
        'steam', 'gaming', 'repair', 'fix', 'library', 'configuration',
        'steam-games', 'steam-library', 'steam-error', 'game-management',
        'steam-repair', 'steam-tool', 'gaming-utility', 'steam-fix',
        'steam-download-error', 'steam-wrong-drive', 'steam-staging-folder'
    ],
)
