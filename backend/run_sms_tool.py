#!/usr/bin/env python3
"""Convenience wrapper script for running the test assessment SMS tool.

Run this script from the backend directory.
Usage: python run_sms_tool.py phone_numbers.txt
"""

import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Run the main script as a module
if __name__ == "__main__":
    import asyncio
    from scripts.test_assessment_sms import main

    exit_code = asyncio.run(main())
    sys.exit(exit_code)
