from pathlib import Path

from setuptools import find_namespace_packages, setup

PROJECT_DIR = Path(__file__).parent
README_PATH = PROJECT_DIR / "README.md"

long_description = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else ""

setup(
    name="file-risk-analyzer",
    version="0.1.0",
    description="Utilities for assessing risk within a source code repository.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OptimizelyPrime/FileRiskAnalyzer",
    packages=find_namespace_packages(
        include=[
            "common",
            "common.*",
            "scan",
            "scan.*",
            "refactor",
            "refactor.*",
        ]
    ),
    package_data={"scan": ["dashboard_template.html"]},
    include_package_data=True,
    install_requires=[
        "GitPython",
        "openai",
        "langchain",
        "pydantic",
        "python-dotenv",
        "langchain-core",
        "radon",
        "pandas",
        "langchain_openai",
        "esprima",
        "fastapi",
        "uvicorn[standard]",
        "google-generativeai",
        "langchain-google-genai",
        "requests",
    ],
    extras_require={
        "dev": ["pytest"],
        "scorecalc": ["MainScoreCalc @ git+https://github.com/OptimizelyPrime/MainScoreCalc.git"],
    },
    entry_points={
        "console_scripts": [
            "file-risk-scan=scan.main:main",
        ]
    },
    python_requires=">=3.9",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
