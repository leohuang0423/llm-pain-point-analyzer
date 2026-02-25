from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llm-pain-point-analyzer",
    version="1.0.0",
    author="leohuang0423",
    author_email="leoclaw@example.com",
    description="A toolkit to solve core pain points for LLMs as first users of APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/leohuang0423/llm-pain-point-analyzer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: OpenClaw",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
    ],
    keywords=["llm", "agent", "ai", "mcp", "openclaw", "permission", "tool-recommendation", "error-diagnosis"],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "llm-ppa=llm_pain_point_analyzer.cli:main",
        ],
    },
)
