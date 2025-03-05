#!/usr/bin/env python3
"""
PDFExPyセットアップスクリプト
"""

import os
from setuptools import setup, find_packages

# パッケージ情報を取得
about = {}
with open(os.path.join("pdfexpy", "__init__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)

# READMEを読み込む
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

# 依存パッケージを読み込む
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="pdfexpy",
    version=about["__version__"],
    description=about["__description__"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=about["__author__"],
    license=about["__license__"],
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pdfexpy=pdfexpy.app:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
) 