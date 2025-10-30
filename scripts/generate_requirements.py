#!/usr/bin/env python3
"""
Generate requirements.txt files from pyproject.toml.

This script extracts dependencies from pyproject.toml and creates:
- requirements.txt: Production dependencies
- requirements-dev.txt: All dependencies including dev
"""

import tomllib
from pathlib import Path


def generate_requirements():
    """Generate requirements files from pyproject.toml."""
    project_root = Path(__file__).parent.parent
    pyproject_path = project_root / "pyproject.toml"
    
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found!")
        return 1
    
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    
    # Get production dependencies
    prod_deps = data.get("project", {}).get("dependencies", [])
    
    # Write requirements.txt
    requirements_path = project_root / "requirements.txt"
    with open(requirements_path, "w") as f:
        f.write("# Auto-generated from pyproject.toml - DO NOT EDIT MANUALLY\n")
        f.write("# Regenerate with: python scripts/generate_requirements.py\n\n")
        for dep in sorted(prod_deps):
            f.write(f"{dep}\n")
    print(f"✓ Generated {requirements_path}")
    
    # Get dev dependencies
    dev_deps = data.get("project", {}).get("optional-dependencies", {}).get("dev", [])
    
    # Write requirements-dev.txt
    requirements_dev_path = project_root / "requirements-dev.txt"
    with open(requirements_dev_path, "w") as f:
        f.write("# Auto-generated from pyproject.toml - DO NOT EDIT MANUALLY\n")
        f.write("# Regenerate with: python scripts/generate_requirements.py\n\n")
        f.write("# Production dependencies\n")
        f.write("-r requirements.txt\n\n")
        f.write("# Development dependencies\n")
        for dep in sorted(dev_deps):
            f.write(f"{dep}\n")
    print(f"✓ Generated {requirements_dev_path}")
    
    return 0


if __name__ == "__main__":
    exit(generate_requirements())