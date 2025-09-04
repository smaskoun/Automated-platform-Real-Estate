# src/services/ab_testing_service.py - FINAL CORRECTED VERSION

import random
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics

# This import is now correct and will work once the model is exposed
from models.ab_test_model import ABTest, ABTestVariation


class ABTestingService:
    """Service for creating and managing A/B tests for social media content"""
    
    def __init__(self):
        self.active_tests = {}  # In production, this would be a database
        self.completed_tests = {}
        
        # ... (all of your existing class methods go here, no changes needed)
        # ...
        # ...
    
    def get_all_tests(self) -> List[Dict]:
        """Get a list of all active and completed tests"""
        all_tests = list(self.active_tests.values()) + list(self.completed_tests.values())
        return [asdict(test) for test in all_tests]

# --- THIS IS THE NEW LINE TO ADD ---
# Create a single, shared instance of the service for the whole application to use.
# The name 'ab_testing_service' must match what the route file tries to import.
ab_testing_service = ABTestingService()
