# -*- coding: utf-8 -*-
"""
AI标书系统安装配置
"""

from setuptools import setup, find_packages

setup(
    name="ai_tender_system",
    version="2.0.0",
    description="AI标书系统 - 智能招标文档处理平台",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "python-docx>=0.8.11",
        "flask>=2.2.0",
        "flask-cors>=4.0.0",
    ],
    extras_require={
        "all": [
            "mammoth>=1.5.1",
            "PyPDF2>=3.0.1", 
            "pdfplumber>=0.7.6",
            "PyMuPDF>=1.21.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ]
    }
)