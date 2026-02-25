#!/usr/bin/env python3
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llm-pain-point-analyzer",
    version="1.0.0",
    author="LeoClaw",
    author_email="",
    description="LLM痛点分析器 - 解决大模型作为第一用户的三大核心痛点",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/llm-pain-point-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.1",
        "pydantic>=1.8.0",
        "typing-extensions>=3.7.4",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.5b2",
            "flake8>=3.9.0",
            "mypy>=0.900",
        ],
    },
    entry_points={
        "console_scripts": [
            "llm-pain-analyze=llm_pain_point_analyzer.permission_analyzer:main",
            "llm-tool-recommend=llm_pain_point_analyzer.tool_recommender:main",
            "llm-error-diagnose=llm_pain_point_analyzer.error_diagnoser:main",
            "llm-permission-verify=llm_pain_point_analyzer.permission_verifier:main",
        ],
    },
    package_data={
        "llm_pain_point_analyzer": [
            "config/*.json",
        ],
    },
    include_package_data=True,
    keywords=[
        "llm",
        "ai",
        "pain-point",
        "permission",
        "tool-recommendation",
        "error-diagnosis",
        "openclaw",
        "ai-assistant",
    ],
    project_urls={
        "Bug Reports": "https://github.com/yourusername/llm-pain-point-analyzer/issues",
        "Source": "https://github.com/yourusername/llm-pain-point-analyzer",
        "Documentation": "https://github.com/yourusername/llm-pain-point-analyzer/blob/main/README.md",
    },
)