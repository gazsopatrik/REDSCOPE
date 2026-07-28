#!/usr/bin/env python3
"""
RedScope Demo Lab Data Seeder
Populates database with sample authorized projects, scopes, targets, scans, and findings for local testing.
"""

import sys
from pathlib import Path

# Ensure backend app package is importable
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

print("[+] RedScope Demo Data Seeder")
print("[+] Note: DEMO DATA – NOT A REAL SECURITY ASSESSMENT")
print("[+] Database initialized with Demo Lab scope.")
