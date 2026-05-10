"""Core diff calculation module."""

import json
from typing import Dict, List, Any, Tuple, Set, Union
from dataclasses import dataclass
from enum import Enum
import difflib


class DiffType(Enum):
    """Types of differences."""
    STRUCTURAL = "structural"
    CONTENT = "content"
    SEMANTIC = "semantic"
    TYPE_MISMATCH = "type_mismatch"


class Severity(Enum):
    """Severity levels for differences."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Difference:
    """Represents a single difference between two JSON objects."""
    
    id: str
    comparison: str
    path: str
    type: DiffType
    severity: Severity
    description: str
    value_a: Any = None
    value_b: Any = None
    impact: str = ""
    recommendation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert difference to dictionary."""
        return {
            "id": self.id,
            "comparison": self.comparison,
            "path": self.path,
            "type": self.type.value,
            "severity": self.severity.value,
            "description": self.description,
            "value_a": self.value_a,
            "value_b": self.value_b,
            "impact": self.impact,
            "recommendation": self.recommendation
        }


class JSONDiffCalculator:
    """Core diff calculation class."""
    
    def __init__(self, config):
        self.config = config
        self.diff_counter = 0
    
    def generate_id(self) -> str:
        """Generate unique difference ID."""
        self.diff_counter += 1
        return f"diff_{self.diff_counter:03d}"
    
    def find_differences(self, obj1: Any, obj2: Any, path: str = "", 
                        comparison: str = "") -> List[Difference]:
        """
        Recursively find differences between two JSON objects.
        """
        differences = []
        
        # Type mismatch check
        if type(obj1) != type(obj2):
            diff = Difference(
                id=self.generate_id(),
                comparison=comparison,
                path=path,
                type=DiffType.TYPE_MISMATCH,
                severity=Severity.HIGH,
                description=f"类型不匹配: {type(obj1).__name__} vs {type(obj2).__name__}",
                value_a=type(obj1).__name__,
                value_b=type(obj2).__name__,
                impact="数据类型不一致可能导致处理错误",
                recommendation="统一数据类型"
            )
            differences.append(diff)
            return differences
        
        # Dictionary comparison
        if isinstance(obj1, dict) and isinstance(obj2, dict):
            all_keys = set(obj1.keys()) | set(obj2.keys())
            
            for key in all_keys:
                if key in self.config.ignore_fields:
                    continue
                    
                new_path = f"{path}.{key}" if path else key
                
                if key in obj1 and key in obj2:
                    # Both have the key, recurse deeper
                    sub_diffs = self.find_differences(
                        obj1[key], obj2[key], new_path, comparison
                    )
                    differences.extend(sub_diffs)
                    
                elif key in obj1:
                    # Key only in obj1
                    diff = Difference(
                        id=self.generate_id(),
                        comparison=comparison,
                        path=new_path,
                        type=DiffType.STRUCTURAL,
                        severity=self._assess_severity("field_missing"),
                        description=f"字段缺失: {new_path} (仅在第一个文件中存在)",
                        value_a=obj1[key],
                        value_b=None,
                        impact="数据结构不完整",
                        recommendation="检查字段是否应该存在"
                    )
                    differences.append(diff)
                    
                else:
                    # Key only in obj2
                    diff = Difference(
                        id=self.generate_id(),
                        comparison=comparison,
                        path=new_path,
                        type=DiffType.STRUCTURAL,
                        severity=self._assess_severity("field_addition"),
                        description=f"字段新增: {new_path} (仅在第二个文件中存在)",
                        value_a=None,
                        value_b=obj2[key],
                        impact="数据结构扩展",
                        recommendation="确认是否为合法新增字段"
                    )
                    differences.append(diff)
        
        # List comparison
        elif isinstance(obj1, list) and isinstance(obj2, list):
            if len(obj1) != len(obj2):
                diff = Difference(
                    id=self.generate_id(),
                    comparison=comparison,
                    path=path,
                    type=DiffType.STRUCTURAL,
                    severity=self._assess_severity("array_length"),
                    description=f"数组长度不同: {path} ({len(obj1)} vs {len(obj2)})",
                    value_a=len(obj1),
                    value_b=len(obj2),
                    impact="数据量不一致",
                    recommendation="检查数组元素数量"
                )
                differences.append(diff)
            
            # Compare elements up to the minimum length
            for i in range(min(len(obj1), len(obj2))):
                new_path = f"{path}[{i}]"
                sub_diffs = self.find_differences(
                    obj1[i], obj2[i], new_path, comparison
                )
                differences.extend(sub_diffs)
        
        # Primitive value comparison
        elif obj1 != obj2:
            severity = self._assess_severity("value_mismatch", obj1, obj2)
            diff_type = self._determine_diff_type(obj1, obj2)
            
            diff = Difference(
                id=self.generate_id(),
                comparison=comparison,
                path=path,
                type=diff_type,
                severity=severity,
                description=f"值不匹配: {path}",
                value_a=obj1,
                value_b=obj2,
                impact=self._assess_impact(path, obj1, obj2),
                recommendation=self._generate_recommendation(path, obj1, obj2)
            )
            differences.append(diff)
        
        return differences
    
    def _assess_severity(self, diff_type: str, val1=None, val2=None) -> Severity:
        """Assess severity based on difference type and values."""
        if diff_type in ["type_mismatch", "array_length"]:
            return Severity.HIGH
        
        if diff_type == "field_missing":
            # Check if missing field is critical
            return Severity.MEDIUM
        
        if diff_type == "value_mismatch":
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numeric differences
                if abs(val1 - val2) / max(abs(val1), abs(val2), 1) > self.config.critical_threshold:
                    return Severity.CRITICAL
                elif abs(val1 - val2) / max(abs(val1), abs(val2), 1) > self.config.high_threshold:
                    return Severity.HIGH
                elif abs(val1 - val2) / max(abs(val1), abs(val2), 1) > self.config.medium_threshold:
                    return Severity.MEDIUM
                else:
                    return Severity.LOW
            
            # String differences
            if isinstance(val1, str) and isinstance(val2, str):
                similarity = difflib.SequenceMatcher(None, val1, val2).ratio()
                if similarity < 0.3:
                    return Severity.HIGH
                elif similarity < 0.7:
                    return Severity.MEDIUM
                else:
                    return Severity.LOW
        
        return Severity.MEDIUM
    
    def _determine_diff_type(self, val1, val2) -> DiffType:
        """Determine the type of difference."""
        if isinstance(val1, (dict, list)) or isinstance(val2, (dict, list)):
            return DiffType.STRUCTURAL
        
        # Check for semantic differences (e.g., email vs phone number pattern)
        if isinstance(val1, str) and isinstance(val2, str):
            if '@' in val1 or '@' in val2:
                return DiffType.SEMANTIC
            if any(c.isdigit() for c in val1) or any(c.isdigit() for c in val2):
                return DiffType.SEMANTIC
        
        return DiffType.CONTENT
    
    def _assess_impact(self, path: str, val1, val2) -> str:
        """Assess the impact of the difference."""
        path_lower = path.lower()
        
        if any(keyword in path_lower for keyword in ['price', 'amount', 'total', 'cost']):
            return "直接影响财务计算"
        elif any(keyword in path_lower for keyword in ['email', 'phone', 'address']):
            return "影响联系信息准确性"
        elif any(keyword in path_lower for keyword in ['id', 'code', 'key']):
            return "影响数据唯一性和关联性"
        elif any(keyword in path_lower for keyword in ['date', 'time', 'deadline']):
            return "影响时间相关业务逻辑"
        
        return "影响数据一致性"
    
    def _generate_recommendation(self, path: str, val1, val2) -> str:
        """Generate recommendation based on difference."""
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            return "检查数值计算逻辑或数据源"
        elif isinstance(val1, str) and isinstance(val2, str):
            if '@' in val1 or '@' in val2:
                return "验证邮箱地址格式和域名"
            elif any(c.isdigit() for c in val1) or any(c.isdigit() for c in val2):
                return "检查电话号码或编码格式"
            else:
                return "统一文本格式和编码"
        elif isinstance(val1, bool) or isinstance(val2, bool):
            return "确认布尔值逻辑"
        
        return "检查数据源和转换逻辑"