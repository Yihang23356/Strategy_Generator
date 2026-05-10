#!/usr/bin/env python3
"""Main script for JSON diff analysis."""

import os
import sys
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from json_diff_analyzer import JSONDiffAnalyzer, AnalysisConfig, ReportGenerator


def main():
    """Main execution function."""
    print("JSON 差异分析系统")
    print("=" * 60)
    
    # Configuration
    config = AnalysisConfig(
        input_files=[
            "input/uploads/input_a_input_a.json",
            "input/uploads/input_b_input_b.json", 
            "input/uploads/input_c_input_c.json"
        ],
        standard_answer_file="input/uploads/standard_standard_answer.json",
        output_file="output/review_round_1/result.json",
        
        # Analysis parameters
        max_nesting_depth=10,
        ignore_case=False,
        numeric_tolerance=0.001,
        ignore_fields=["metadata", "timestamp"],  # Fields to ignore
        
        # Severity thresholds
        critical_threshold=0.5,
        high_threshold=0.3,
        medium_threshold=0.1,
        
        # Verification settings
        manual_check_percentage=0.2,
        random_seed=42
    )
    
    # Create analyzer
    analyzer = JSONDiffAnalyzer(config)
    
    try:
        # Step 1: Load data
        print("\n[步骤 1] 加载数据文件...")
        analyzer.load_data()
        
        # Check if data was loaded successfully
        loaded_files = [f for f, data in analyzer.data.items() if data]
        if not loaded_files:
            print("错误: 没有成功加载任何数据文件")
            return False
        
        print(f"成功加载 {len(loaded_files)} 个文件")
        
        # Step 2: Perform analysis
        print("\n[步骤 2] 执行差异分析...")
        analyzer.analyze()
        
        # Step 3: Save results
        print("\n[步骤 3] 保存分析结果...")
        analyzer.save_results()
        
        # Step 4: Generate reports
        print("\n[步骤 4] 生成报告...")
        results = analyzer.get_results()
        
        # Generate text report
        text_report = ReportGenerator.generate_text_report(results)
        text_report_path = "output/review_round_1/report.txt"
        os.makedirs(os.path.dirname(text_report_path), exist_ok=True)
        with open(text_report_path, 'w', encoding='utf-8') as f:
            f.write(text_report)
        print(f"文本报告已保存: {text_report_path}")
        
        # Generate markdown report
        md_report = ReportGenerator.generate_markdown_report(results)
        md_report_path = "output/review_round_1/report.md"
        with open(md_report_path, 'w', encoding='utf-8') as f:
            f.write(md_report)
        print(f"Markdown 报告已保存: {md_report_path}")
        
        # Step 5: Display summary
        print("\n[步骤 5] 分析完成摘要")
        print("-" * 40)
        summary = results.get("summary", {})
        print(f"总差异数: {summary.get('total_differences', 0)}")
        
        by_severity = summary.get('by_severity', {})
        for severity, count in by_severity.items():
            print(f"{severity.upper()} 级别差异: {count}")
        
        print(f"\n详细结果已保存到: {config.output_file}")
        
        return True
        
    except Exception as e:
        print(f"\n错误: 分析过程中发生异常")
        print(f"异常类型: {type(e).__name__}")
        print(f"异常信息: {str(e)}")
        
        # Save error information
        error_result = {
            "metadata": {
                "analysis_timestamp": datetime.now().isoformat(),
                "input_files": config.input_files,
                "standard_answer": config.standard_answer_file,
                "status": "error",
                "error": str(e)
            },
            "summary": {
                "total_differences": 0,
                "by_comparison": {},
                "by_severity": {},
                "by_type": {}
            },
            "detailed_differences": [],
            "consistency_analysis": {},
            "verification": {
                "manual_check_samples": [],
                "verification_passed": False,
                "notes": f"分析失败: {str(e)}"
            }
        }
        
        # Save error result
        os.makedirs(os.path.dirname(config.output_file), exist_ok=True)
        with open(config.output_file, 'w', encoding='utf-8') as f:
            json.dump(error_result, f, ensure_ascii=False, indent=2)
        
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)