#!/usr/bin/env python3
"""Verify the analysis results."""

import json
import os
import sys

def verify_result_file():
    """Verify the result file exists and has valid structure."""
    result_file = "output/review_round_1/result.json"
    
    if not os.path.exists(result_file):
        print(f"错误: 结果文件不存在: {result_file}")
        return False
    
    try:
        with open(result_file, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        # Check required fields
        required_fields = ['metadata', 'summary', 'detailed_differences']
        for field in required_fields:
            if field not in result:
                print(f"错误: 结果文件缺少必需字段: {field}")
                return False
        
        # Check metadata
        metadata = result.get('metadata', {})
        if 'analysis_timestamp' not in metadata:
            print("警告: 元数据缺少分析时间戳")
        
        # Check summary
        summary = result.get('summary', {})
        total_differences = summary.get('total_differences', 0)
        print(f"总差异数: {total_differences}")
        
        # Check detailed differences
        differences = result.get('detailed_differences', [])
        print(f"详细差异记录数: {len(differences)}")
        
        # Check if detailed count matches summary
        if len(differences) != total_differences:
            print(f"警告: 详细差异数({len(differences)})与汇总数({total_differences})不匹配")
        
        # Check file structure
        print("\n结果文件结构验证:")
        print(f"  metadata: {len(metadata)} 个字段")
        print(f"  summary: {len(summary)} 个字段")
        print(f"  detailed_differences: {len(differences)} 条记录")
        
        if 'consistency_analysis' in result:
            print(f"  consistency_analysis: 存在")
        
        if 'verification' in result:
            print(f"  verification: 存在")
        
        # Check output file paths
        report_txt = "output/review_round_1/report.txt"
        report_md = "output/review_round_1/report.md"
        
        if os.path.exists(report_txt):
            with open(report_txt, 'r', encoding='utf-8') as f:
                txt_content = f.read()
            print(f"\n文本报告: {len(txt_content)} 字符")
        
        if os.path.exists(report_md):
            with open(report_md, 'r', encoding='utf-8') as f:
                md_content = f.read()
            print(f"Markdown报告: {len(md_content)} 字符")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"错误: 结果文件不是有效的JSON: {e}")
        return False
    except Exception as e:
        print(f"错误: 验证过程中发生异常: {e}")
        return False

def main():
    """Main verification function."""
    print("JSON差异分析结果验证")
    print("=" * 50)
    
    success = verify_result_file()
    
    if success:
        print("\n[PASS] 验证通过: 结果文件格式正确")
        return 0
    else:
        print("\n[FAIL] 验证失败: 结果文件存在问题")
        return 1

if __name__ == "__main__":
    sys.exit(main())