from setuptools import setup, find_packages

setup(
    name="tasktree",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "pydantic>=2.0.0",
        "appdirs>=1.4.4",
    ],
    entry_points={
        "console_scripts": [
            "tasktree=tasktree.cli:app",
        ],
    },
    author="TaskTree Developers",
    description="A tree-structured task management CLI tool",
    keywords="cli task management tree",
    python_requires=">=3.8",
)