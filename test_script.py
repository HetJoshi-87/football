#!/usr/bin/env python3
"""Test script to debug the ultimate_football_scraper.py issue"""

import sys
import traceback

try:
    print("Testing imports...")
    import os
    print("✅ os imported")
    
    import time
    print("✅ time imported")
    
    import random
    print("✅ random imported")
    
    import json
    print("✅ json imported")
    
    import subprocess
    print("✅ subprocess imported")
    
    from typing import List, Dict, Optional
    print("✅ typing imported")
    
    from bs4 import BeautifulSoup
    print("✅ BeautifulSoup imported")
    
    import requests
    print("✅ requests imported")
    
    print("\nTesting file existence...")
    if os.path.exists("step5(3-6).txt"):
        print("✅ step5(3-6).txt exists")
    else:
        print("❌ step5(3-6).txt not found")
    
    print("\nTesting ultimate_football_scraper import...")
    import ultimate_football_scraper
    print("✅ ultimate_football_scraper imported successfully")
    
    print("\nTesting main function...")
    ultimate_football_scraper.main()
    
except Exception as e:
    print(f"\n❌ Error occurred:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
