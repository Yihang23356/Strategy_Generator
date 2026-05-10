"""Configuration module for JSON diff analysis."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional


@dataclass
class AnalysisConfig:
    """Configuration for JSON diff analysis."""
    
    input_files: List[str]
    standard_answer_file: str
    output_file: str
    
    # Analysis parameters
    max_nesting_depth: int = 10
    ignore_case: bool = False
    numeric_tolerance: float = 0.001
    ignore_fields: List[str] = field(default_factory=list)
    
    # Severity thresholds
    critical_threshold: float = 0.5
    high_threshold: float = 0.3
    medium_threshold: float = 0.1
    
    # Verification settings
    manual_check_percentage: float = 0.2
    random_seed: Optional[int] = 42
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            'input_files': self.input_files,
            'standard_answer_file': self.standard_answer_file,
            'output_file': self.output_file,
            'max_nesting_depth': self.max_nesting_depth,
            'ignore_case': self.ignore_case,
            'numeric_tolerance': self.numeric_tolerance,
            'ignore_fields': self.ignore_fields,
            'critical_threshold': self.critical_threshold,
            'high_threshold': self.high_threshold,
            'medium_threshold': self.medium_threshold,
            'manual_check_percentage': self.manual_check_percentage,
            'random_seed': self.random_seed
        }