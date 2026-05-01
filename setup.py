"""NickyData package setup."""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="nickydata",
    version="1.0.0",
    author="Nicholas Anderson",
    description="Reproducible research pipeline architecture (8-phase: S/L/P/V/M/A/O/E)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andenick/nickydata",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "nickydata=nickydata.scaffold:main",
        ],
    },
)
