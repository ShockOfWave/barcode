#!/usr/bin/env python3
"""
Setup script for afm_tda_tools package.
"""

from setuptools import setup, find_packages
import os

# Читаем README для long_description
def read_readme():
    """Читаем README.md файл."""
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Читаем requirements из pyproject.toml
def get_requirements():
    """Получаем зависимости из pyproject.toml."""
    return [
        "gudhi>=3.11.0",
        "matplotlib>=3.10.1",
        "numpy>=2.2.3",
        "pandas>=2.2.3",
        "rich>=13.9.4",
        "ripser>=0.6.12",
        "ruff>=0.9.10",
        "simple-term-menu>=1.6.6",
        "statsmodels>=0.14.4",
    ]

setup(
    name="afm-tda-tools",
    version="0.1.0",
    author="ShockOfWave",
    author_email="shockofwave90@gmail.com",
    description="Topological Data Analysis tools for AFM data processing",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ShockOfWave/barcode",
    project_urls={
        "Bug Reports": "https://github.com/ShockOfWave/barcode/issues",
        "Source": "https://github.com/ShockOfWave/barcode",
        "Documentation": "https://github.com/ShockOfWave/barcode#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=get_requirements(),
    extras_require={
        "dev": [
            "pytest>=8.3.5",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "isort>=5.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "afm-tda-tools=afm_tda_tools.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "afm_tda_tools": ["data/*"],
    },
    keywords=[
        "topological-data-analysis",
        "afm",
        "atomic-force-microscopy",
        "persistent-homology",
        "vietoris-rips",
        "betti-numbers",
        "gudhi",
        "materials-science",
        "surface-analysis",
    ],
    license="MIT",
    zip_safe=False,
) 