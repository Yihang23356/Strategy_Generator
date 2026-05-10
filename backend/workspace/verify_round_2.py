#!/usr/bin/env python3
"""Verification script for round 2 results."""

import json
import os
import sys


def verify_results():
    """Verify round 2 results meet the requirements."""
    print("第二轮审核结果验证")
    print("=" * 60)
    
    # Load results
    result_file = "output/review_round_2/result.json"
    
    if not os.path.exists(result_file):
        print(f"错误: 结果文件不存在: {result_file}")
        return False
    
    try:
        with open(result_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        print("[OK] 成功加载结果文件")
        
        # Check required sections
        required_sections = ['metadata', 'summary', 'detailed_differences', 
                           'consistency_analysis', 'verification']
        
        for section in required_sections:
            if section not in results:
                print(f"[ERROR] 缺失必要部分: {section}")
                return False
        
        print("[OK] 所有必要部分都存在")
        
        # Check metadata
        metadata = results['metadata']
        required_metadata = ['analysis_timestamp', 'input_files', 'standard_answer']
        
        for field in required_metadata:
            if field not in metadata:
                print(f"[ERROR] metadata 中缺失字段: {field}")
                return False
        
        print("[OK] metadata 完整")
        
        # Check summary
        summary = results['summary']
        required_summary = ['total_differences', 'by_comparison', 'by_severity', 'by_type']
        
        for field in required_summary:
            if field not in summary:
                print(f"[ERROR] summary 中缺失字段: {field}")
                return False
        
        print("[OK] summary 完整")
        
        # Check detailed differences
        detailed_diffs = results['detailed_differences']
        
        if not isinstance(detailed_diffs, list):
            print("[ERROR] detailed_differences 不是列表")
            return False
        
        if len(detailed_diffs) == 0:
            print("[ERROR] detailed_differences 为空")
            return False
        
        # Check first difference for required fields
        if detailed_diffs:
            first_diff = detailed_diffs[0]
            required_diff_fields = ['id', 'comparison', 'path', 'type', 'severity', 
                                  'description', 'impact']
            
            for field in required_diff_fields:
                if field not in first_diff:
                    print(f"[ERROR] 差异记录中缺失字段: {field}")
                    return False
        
        print(f"[OK] 详细差异记录完整 (共 {len(detailed_diffs)} 条)")
        
        # Check consistency analysis
        consistency = results['consistency_analysis']
        required_consistency = ['consistent_across_all', 'inconsistent_across_all',
                              'closest_to_standard', 'most_deviated']
        
        for field in required_consistency:
            if field not in consistency:
                print(f"[ERROR] consistency_analysis 中缺失字段: {field}")
                return False
        
        print("[OK] consistency_analysis 完整")
        
        # Check verification
        verification = results['verification']
        required_verification = ['manual_check_samples', 'verification_passed', 'notes']
        
        for field in required_verification:
            if field not in verification:
                print(f"[ERROR] verification 中缺失字段: {field}")
                return False
        
        print("[OK] verification 完整")
        
        # Check output files
        required_files = [
            "output/review_round_2/result.json",
            "output/review_round_2/report.txt",
            "output/review_round_2/report.md",
            "output/review_round_2/execution.log"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            print(f"[ERROR] 缺失输出文件: {missing_files}")
            return False
        
        print("[OK] 所有输出文件都存在")
        
        # Check content quality
        print("\n内容质量检查:")
        
        # Check if differences are meaningful
        total_diffs = summary['total_differences']
        if total_diffs > 0:
            print(f"[OK] 发现 {total_diffs} 个差异")
        else:
            print("[WARN] 未发现任何差异")
        
        # Check severity distribution
        by_severity = summary['by_severity']
        print(f"[OK] 严重程度分布:")
        for severity, count in by_severity.items():
            print(f"  - {severity}: {count}")
        
        # Check consistency analysis results
        closest = consistency['closest_to_standard']
        most_deviated = consistency['most_deviated']
        print(f"[OK] 最接近标准答案: {closest}")
        print(f"[OK] 偏离最大: {most_deviated}")
        
        # Check verification results
        verification_passed = verification['verification_passed']
        if verification_passed:
            print("[OK] 验证通过")
        else:
            print("[ERROR] 验证失败")
            return False
        
        print("\n" + "=" * 60)
        print("[SUCCESS] 所有验证通过！第二轮审核结果符合要求。")
        return True
        
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 解析错误: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] 验证过程中发生错误: {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    success = verify_results()
    sys.exit(0 if success else 1)