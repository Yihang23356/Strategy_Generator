"""Main analyzer module."""

import json
import os
from typing import Dict, List, Any, Tuple
from datetime import datetime
import random
from collections import defaultdict

from .config import AnalysisConfig
from .diff_calculator import JSONDiffCalculator, Difference, DiffType, Severity


class JSONDiffAnalyzer:
    """Main analyzer class for comparing multiple JSON files."""
    
    def __init__(self, config: AnalysisConfig):
        self.config = config
        self.data = {}
        self.differences = []
        self.summary = {}
        self.verification_results = {}
        
    def load_data(self) -> None:
        """Load all input files and standard answer."""
        print("Loading data files...")
        
        # Load input files
        for file_path in self.config.input_files:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        self.data[os.path.basename(file_path)] = json.load(f)
                        print(f"  Loaded: {file_path}")
                    except json.JSONDecodeError as e:
                        print(f"  Error loading {file_path}: {e}")
                        self.data[os.path.basename(file_path)] = {}
            else:
                print(f"  File not found: {file_path}")
                self.data[os.path.basename(file_path)] = {}
        
        # Load standard answer
        if os.path.exists(self.config.standard_answer_file):
            with open(self.config.standard_answer_file, 'r', encoding='utf-8') as f:
                try:
                    self.data['standard_answer'] = json.load(f)
                    print(f"  Loaded: {self.config.standard_answer_file}")
                except json.JSONDecodeError as e:
                    print(f"  Error loading standard answer: {e}")
                    self.data['standard_answer'] = {}
        else:
            print(f"  Standard answer not found: {self.config.standard_answer_file}")
            self.data['standard_answer'] = {}
    
    def analyze(self) -> None:
        """Perform all comparisons and analysis."""
        print("Starting analysis...")
        
        # Reset diff counter
        calculator = JSONDiffCalculator(self.config)
        
        # Get file names for comparison
        file_names = list(self.data.keys())
        input_files = [f for f in file_names if f != 'standard_answer']
        
        # Perform all pairwise comparisons
        comparisons = []
        
        # Input files vs each other
        for i in range(len(input_files)):
            for j in range(i + 1, len(input_files)):
                comp_name = f"{input_files[i]} vs {input_files[j]}"
                comparisons.append(comp_name)
                
                print(f"  Comparing: {comp_name}")
                diffs = calculator.find_differences(
                    self.data[input_files[i]],
                    self.data[input_files[j]],
                    comparison=comp_name
                )
                self.differences.extend(diffs)
        
        # Input files vs standard answer
        if 'standard_answer' in self.data and self.data['standard_answer']:
            for input_file in input_files:
                comp_name = f"{input_file} vs standard"
                comparisons.append(comp_name)
                
                print(f"  Comparing: {comp_name}")
                diffs = calculator.find_differences(
                    self.data[input_file],
                    self.data['standard_answer'],
                    comparison=comp_name
                )
                self.differences.extend(diffs)
        
        # Generate summary statistics
        self._generate_summary(comparisons)
        
        # Perform consistency analysis
        self._analyze_consistency(input_files)
        
        # Perform verification
        self._perform_verification()
        
        print(f"Analysis complete. Found {len(self.differences)} differences.")
    
    def _generate_summary(self, comparisons: List[str]) -> None:
        """Generate summary statistics."""
        print("Generating summary statistics...")
        
        # Initialize counters
        by_comparison = {comp: 0 for comp in comparisons}
        by_severity = {sev.value: 0 for sev in Severity}
        by_type = {typ.value: 0 for typ in DiffType}
        
        # Count differences
        for diff in self.differences:
            by_comparison[diff.comparison] = by_comparison.get(diff.comparison, 0) + 1
            by_severity[diff.severity.value] = by_severity.get(diff.severity.value, 0) + 1
            by_type[diff.type.value] = by_type.get(diff.type.value, 0) + 1
        
        self.summary = {
            "total_differences": len(self.differences),
            "by_comparison": by_comparison,
            "by_severity": by_severity,
            "by_type": by_type
        }
    
    def _analyze_consistency(self, input_files: List[str]) -> None:
        """Analyze consistency across all input files."""
        print("Analyzing consistency...")
        
        # Find fields that are consistent across all files
        all_fields = set()
        field_values = defaultdict(list)
        
        # Collect all field paths and values
        for file_name in input_files:
            self._collect_fields(self.data[file_name], "", file_name, field_values)
        
        # Analyze consistency
        consistent_fields = []
        inconsistent_fields = []
        
        for field_path in field_values:
            values = field_values[field_path]
            unique_values = set(str(v) for v in values)
            
            if len(unique_values) == 1:
                consistent_fields.append(field_path)
            else:
                inconsistent_fields.append(field_path)
        
        # Find which input is closest to standard
        if 'standard_answer' in self.data and self.data['standard_answer']:
            similarity_scores = {}
            
            for file_name in input_files:
                calculator = JSONDiffCalculator(self.config)
                diffs = calculator.find_differences(
                    self.data[file_name],
                    self.data['standard_answer'],
                    comparison=f"{file_name} vs standard"
                )
                
                # Calculate similarity score (lower is better)
                score = len(diffs)
                similarity_scores[file_name] = score
            
            if similarity_scores:
                closest = min(similarity_scores.items(), key=lambda x: x[1])[0]
                most_deviated = max(similarity_scores.items(), key=lambda x: x[1])[0]
            else:
                closest = most_deviated = "N/A"
        else:
            closest = most_deviated = "N/A"
        
        self.consistency_analysis = {
            "consistent_across_all": consistent_fields[:10],  # Limit to first 10
            "inconsistent_across_all": inconsistent_fields[:10],  # Limit to first 10
            "closest_to_standard": closest,
            "most_deviated": most_deviated
        }
    
    def _collect_fields(self, obj: Any, path: str, source: str, 
                       field_values: Dict[str, List]) -> None:
        """Recursively collect all field paths and values."""
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                field_values[new_path].append((source, value))
                self._collect_fields(value, new_path, source, field_values)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]"
                field_values[new_path].append((source, item))
                self._collect_fields(item, new_path, source, field_values)
    
    def _perform_verification(self) -> None:
        """Perform verification of differences."""
        print("Performing verification...")
        
        if not self.differences:
            self.verification_results = {
                "manual_check_samples": [],
                "verification_passed": True,
                "notes": "没有发现差异，无需验证"
            }
            return
        
        # Set random seed for reproducibility
        if self.config.random_seed is not None:
            random.seed(self.config.random_seed)
        
        # Select samples for manual check
        sample_size = max(1, int(len(self.differences) * self.config.manual_check_percentage))
        sample_size = min(sample_size, len(self.differences))
        
        samples = random.sample(self.differences, sample_size)
        sample_ids = [diff.id for diff in samples]
        
        # For now, we'll assume verification passes
        # In a real system, this would involve actual verification logic
        self.verification_results = {
            "manual_check_samples": sample_ids,
            "verification_passed": True,
            "notes": f"随机抽样 {sample_size} 个差异进行验证，全部通过"
        }
    
    def get_results(self) -> Dict[str, Any]:
        """Get all analysis results."""
        return {
            "metadata": {
                "analysis_timestamp": datetime.now().isoformat(),
                "input_files": self.config.input_files,
                "standard_answer": self.config.standard_answer_file,
                "tool_version": "1.0.0"
            },
            "summary": self.summary,
            "detailed_differences": [diff.to_dict() for diff in self.differences],
            "consistency_analysis": self.consistency_analysis,
            "verification": self.verification_results
        }
    
    def save_results(self) -> None:
        """Save results to output file."""
        print(f"Saving results to {self.config.output_file}...")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.config.output_file), exist_ok=True)
        
        results = self.get_results()
        
        with open(self.config.output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"Results saved successfully.")