"""Report generation module."""

import json
from typing import Dict, List, Any
from datetime import datetime


class ReportGenerator:
    """Generate human-readable reports from analysis results."""
    
    @staticmethod
    def generate_text_report(results: Dict[str, Any], include_examples: bool = True) -> str:
        """Generate a text format report.
        
        Args:
            results: Analysis results dictionary
            include_examples: Whether to include example differences
        """
        report = []
        report.append("=" * 80)
        report.append("JSON 差异分析报告")
        report.append("=" * 80)
        report.append("")
        
        # Metadata
        metadata = results.get("metadata", {})
        report.append(f"分析时间: {metadata.get('analysis_timestamp', 'N/A')}")
        report.append(f"输入文件: {', '.join(metadata.get('input_files', []))}")
        report.append(f"标准答案: {metadata.get('standard_answer', 'N/A')}")
        report.append("")
        
        # Summary
        summary = results.get("summary", {})
        report.append("分析摘要")
        report.append("-" * 40)
        report.append(f"总差异数: {summary.get('total_differences', 0)}")
        report.append("")
        
        # By comparison
        report.append("按对比分组:")
        by_comparison = summary.get('by_comparison', {})
        for comp, count in by_comparison.items():
            report.append(f"  {comp}: {count} 个差异")
        report.append("")
        
        # By severity
        report.append("按严重程度:")
        by_severity = summary.get('by_severity', {})
        for sev, count in by_severity.items():
            report.append(f"  {sev}: {count} 个差异")
        report.append("")
        
        # By type
        report.append("按差异类型:")
        by_type = summary.get('by_type', {})
        for typ, count in by_type.items():
            report.append(f"  {typ}: {count} 个差异")
        report.append("")
        
        # Consistency analysis
        consistency = results.get("consistency_analysis", {})
        report.append("一致性分析")
        report.append("-" * 40)
        report.append(f"最接近标准答案: {consistency.get('closest_to_standard', 'N/A')}")
        report.append(f"偏离最大: {consistency.get('most_deviated', 'N/A')}")
        report.append("")
        
        consistent_fields = consistency.get('consistent_across_all', [])
        if consistent_fields:
            report.append(f"完全一致的字段 ({len(consistent_fields)} 个):")
            for field in consistent_fields[:5]:  # Show first 5
                report.append(f"  - {field}")
            if len(consistent_fields) > 5:
                report.append(f"  ... 还有 {len(consistent_fields) - 5} 个字段")
        report.append("")
        
        # Example differences
        detailed_diffs = results.get("detailed_differences", [])
        
        if include_examples and detailed_diffs:
            # Group by severity
            severity_order = ['critical', 'high', 'medium', 'low']
            
            for severity in severity_order:
                diffs_by_severity = [d for d in detailed_diffs if d.get('severity') == severity]
                
                if diffs_by_severity:
                    report.append(f"{severity.upper()} 级别差异示例")
                    report.append("-" * 40)
                    
                    # Show first 3 examples for each severity
                    for diff in diffs_by_severity[:3]:
                        report.append(f"ID: {diff.get('id', 'N/A')}")
                        report.append(f"对比: {diff.get('comparison', 'N/A')}")
                        report.append(f"路径: {diff.get('path', 'N/A')}")
                        report.append(f"类型: {diff.get('type', 'N/A')}")
                        
                        # Show values if they exist
                        if 'value_a' in diff and 'value_b' in diff:
                            report.append(f"值A: {diff['value_a']}")
                            report.append(f"值B: {diff['value_b']}")
                        elif 'actual_value' in diff and 'expected_value' in diff:
                            report.append(f"实际值: {diff['actual_value']}")
                            report.append(f"期望值: {diff['expected_value']}")
                        
                        report.append(f"描述: {diff.get('description', 'N/A')}")
                        report.append(f"影响: {diff.get('impact', 'N/A')}")
                        if diff.get('recommendation'):
                            report.append(f"建议: {diff.get('recommendation', 'N/A')}")
                        report.append("")
                    
                    if len(diffs_by_severity) > 3:
                        report.append(f"... 还有 {len(diffs_by_severity) - 3} 个 {severity} 级别差异")
                        report.append("")
        
        # Verification
        verification = results.get("verification", {})
        report.append("验证结果")
        report.append("-" * 40)
        report.append(f"验证通过: {verification.get('verification_passed', False)}")
        report.append(f"抽样检查: {len(verification.get('manual_check_samples', []))} 个样本")
        report.append(f"备注: {verification.get('notes', 'N/A')}")
        report.append("")
        
        report.append("=" * 80)
        report.append("报告生成完成")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    @staticmethod
    def generate_markdown_report(results: Dict[str, Any], include_examples: bool = True) -> str:
        """Generate a markdown format report.
        
        Args:
            results: Analysis results dictionary
            include_examples: Whether to include example differences
        """
        report = []
        report.append("# JSON 差异分析报告")
        report.append("")
        
        # Metadata
        metadata = results.get("metadata", {})
        report.append("## 元数据")
        report.append(f"- **分析时间**: {metadata.get('analysis_timestamp', 'N/A')}")
        report.append(f"- **输入文件**: {', '.join(metadata.get('input_files', []))}")
        report.append(f"- **标准答案**: {metadata.get('standard_answer', 'N/A')}")
        report.append(f"- **工具版本**: {metadata.get('tool_version', 'N/A')}")
        report.append("")
        
        # Summary
        summary = results.get("summary", {})
        report.append("## 分析摘要")
        report.append(f"**总差异数**: {summary.get('total_differences', 0)}")
        report.append("")
        
        # Summary tables
        report.append("### 按对比分组")
        report.append("| 对比 | 差异数 |")
        report.append("|------|--------|")
        by_comparison = summary.get('by_comparison', {})
        for comp, count in by_comparison.items():
            report.append(f"| {comp} | {count} |")
        report.append("")
        
        report.append("### 按严重程度")
        report.append("| 严重程度 | 差异数 |")
        report.append("|----------|--------|")
        by_severity = summary.get('by_severity', {})
        for sev, count in by_severity.items():
            report.append(f"| {sev} | {count} |")
        report.append("")
        
        report.append("### 按差异类型")
        report.append("| 类型 | 差异数 |")
        report.append("|------|--------|")
        by_type = summary.get('by_type', {})
        for typ, count in by_type.items():
            report.append(f"| {typ} | {count} |")
        report.append("")
        
        # Consistency analysis
        consistency = results.get("consistency_analysis", {})
        report.append("## 一致性分析")
        report.append(f"- **最接近标准答案**: `{consistency.get('closest_to_standard', 'N/A')}`")
        report.append(f"- **偏离最大**: `{consistency.get('most_deviated', 'N/A')}`")
        report.append("")
        
        # Example differences
        detailed_diffs = results.get("detailed_differences", [])
        
        if include_examples and detailed_diffs:
            # Group by severity
            severity_order = ['critical', 'high', 'medium', 'low']
            
            for severity in severity_order:
                diffs_by_severity = [d for d in detailed_diffs if d.get('severity') == severity]
                
                if diffs_by_severity:
                    report.append(f"## {severity.upper()} 级别差异示例")
                    report.append("")
                    
                    # Show first 3 examples for each severity
                    for i, diff in enumerate(diffs_by_severity[:3], 1):
                        report.append(f"### 示例 {i}: {diff.get('id', 'N/A')}")
                        report.append(f"- **对比**: {diff.get('comparison', 'N/A')}")
                        report.append(f"- **路径**: `{diff.get('path', 'N/A')}`")
                        report.append(f"- **类型**: {diff.get('type', 'N/A')}")
                        report.append(f"- **严重程度**: **{severity.upper()}**")
                        
                        # Show values if they exist
                        if 'value_a' in diff and 'value_b' in diff:
                            report.append(f"- **值A**: `{diff['value_a']}`")
                            report.append(f"- **值B**: `{diff['value_b']}`")
                        elif 'actual_value' in diff and 'expected_value' in diff:
                            report.append(f"- **实际值**: `{diff['actual_value']}`")
                            report.append(f"- **期望值**: `{diff['expected_value']}`")
                        
                        report.append(f"- **描述**: {diff.get('description', 'N/A')}")
                        report.append(f"- **影响**: {diff.get('impact', 'N/A')}")
                        if diff.get('recommendation'):
                            report.append(f"- **建议**: {diff.get('recommendation', 'N/A')}")
                        report.append("")
                    
                    if len(diffs_by_severity) > 3:
                        report.append(f"*还有 {len(diffs_by_severity) - 3} 个 {severity} 级别差异*")
                        report.append("")
        
        # Verification
        verification = results.get("verification", {})
        report.append("## 验证结果")
        report.append(f"- **验证通过**: {'✅' if verification.get('verification_passed', False) else '❌'}")
        report.append(f"- **抽样检查**: {len(verification.get('manual_check_samples', []))} 个样本")
        report.append(f"- **备注**: {verification.get('notes', 'N/A')}")
        report.append("")
        
        report.append("---")
        report.append("*报告生成完成*")
        
        return "\n".join(report)