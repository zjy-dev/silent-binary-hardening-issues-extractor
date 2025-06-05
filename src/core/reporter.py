"""
报告生成器 - 生成Markdown格式的报告
"""

from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
from src.models.issue import Issue, AnalysisResult


class Reporter:
    """报告生成器"""
    
    def __init__(self, output_dir: str = "output/reports"):
        """
        初始化报告生成器
        
        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_report(self, silent_bugs: List[tuple[Issue, AnalysisResult]], 
                       report_title: str = "Silent Binary Hardening Issues Report") -> str:
        """
        生成完整报告
        
        Args:
            silent_bugs: Silent Bug列表
            report_title: 报告标题
            
        Returns:
            报告文件路径
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"silent_bugs_report_{timestamp}.md"
        filepath = self.output_dir / filename
        
        # 生成报告内容
        content = self._generate_markdown_content(silent_bugs, report_title)
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"报告已生成: {filepath}")
        return str(filepath)
        
    def _generate_markdown_content(self, silent_bugs: List[tuple[Issue, AnalysisResult]], 
                                 report_title: str) -> str:
        """
        生成Markdown内容
        
        Args:
            silent_bugs: Silent Bug列表
            report_title: 报告标题
            
        Returns:
            Markdown内容字符串
        """
        lines = []
        
        # 报告头部
        lines.append(f"# {report_title}")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**发现的Silent Bug数量**: {len(silent_bugs)}")
        lines.append("")
        
        # 摘要统计
        lines.append("## 📊 摘要统计")
        lines.append("")
        
        if silent_bugs:
            # 按严重程度统计
            severity_stats = {}
            source_stats = {}
            mechanism_stats = {}
            
            for issue, result in silent_bugs:
                # 严重程度统计
                severity = result.severity or "未知"
                severity_stats[severity] = severity_stats.get(severity, 0) + 1
                
                # 来源统计
                source = issue.source
                source_stats[source] = source_stats.get(source, 0) + 1
                
                # 防御机制统计
                for mechanism in result.defense_mechanisms:
                    mechanism_stats[mechanism] = mechanism_stats.get(mechanism, 0) + 1
                    
            # 生成统计表格
            lines.append("### 按严重程度分布")
            lines.append("| 严重程度 | 数量 |")
            lines.append("|---------|------|")
            for severity, count in sorted(severity_stats.items()):
                lines.append(f"| {severity} | {count} |")
            lines.append("")
            
            lines.append("### 按来源分布")
            lines.append("| 来源 | 数量 |")
            lines.append("|------|------|")
            for source, count in sorted(source_stats.items()):
                lines.append(f"| {source} | {count} |")
            lines.append("")
            
            if mechanism_stats:
                lines.append("### 涉及的防御机制")
                lines.append("| 防御机制 | 出现次数 |")
                lines.append("|---------|---------|")
                for mechanism, count in sorted(mechanism_stats.items(), key=lambda x: x[1], reverse=True):
                    lines.append(f"| {mechanism} | {count} |")
                lines.append("")
                
        # 详细列表
        lines.append("## 🔍 详细问题列表")
        lines.append("")
        
        if not silent_bugs:
            lines.append("未发现Silent Bug。")
        else:
            for i, (issue, result) in enumerate(silent_bugs, 1):
                lines.append(f"### {i}. {issue.title}")
                lines.append("")
                
                # 基本信息
                lines.append("**基本信息**:")
                lines.append(f"- **来源**: {issue.source}")
                lines.append(f"- **日期**: {issue.date}")
                if issue.author:
                    lines.append(f"- **作者**: {issue.author}")
                lines.append(f"- **链接**: [{issue.url}]({issue.url})")
                lines.append("")
                
                # 分析结果
                lines.append("**分析结果**:")
                lines.append(f"- **置信度**: {result.confidence:.2f}")
                lines.append(f"- **根本原因**: {result.root_cause}")
                lines.append(f"- **严重程度**: {result.severity}")
                lines.append("")
                
                if result.affected_software:
                    lines.append("**受影响软件**:")
                    for software in result.affected_software:
                        lines.append(f"- {software}")
                    lines.append("")
                    
                if result.defense_mechanisms:
                    lines.append("**涉及的防御机制**:")
                    for mechanism in result.defense_mechanisms:
                        lines.append(f"- {mechanism}")
                    lines.append("")
                    
                lines.append("**问题总结**:")
                lines.append(f"{result.summary}")
                lines.append("")
                
                if result.recommendations:
                    lines.append("**修复建议**:")
                    for rec in result.recommendations:
                        lines.append(f"- {rec}")
                    lines.append("")
                    
                lines.append("**原始内容**:")
                lines.append("```")
                lines.append(issue.content[:500] + "..." if len(issue.content) > 500 else issue.content)
                lines.append("```")
                lines.append("")
                lines.append("---")
                lines.append("")
                
        # 报告尾部
        lines.append("## 📋 说明")
        lines.append("")
        lines.append("本报告由 Silent Binary Hardening Issues Extractor 自动生成。")
        lines.append("")
        lines.append("**Silent Bug** 是指不会引起程序运行异常，但会降低安全保障的防御缺失或失效问题，")
        lines.append("包括但不限于:")
        lines.append("- Stack Canary (SSP) 未启用")
        lines.append("- PIE (Position Independent Executable) 缺失")
        lines.append("- RELRO (Read-Only Relocations) 未配置")
        lines.append("- CFI (Control Flow Integrity) 失效")
        lines.append("- 其他二进制防御机制配置错误")
        lines.append("")
        
        return "\n".join(lines)
        
    def generate_summary_json(self, silent_bugs: List[tuple[Issue, AnalysisResult]]) -> str:
        """
        生成JSON格式的摘要
        
        Args:
            silent_bugs: Silent Bug列表
            
        Returns:
            JSON文件路径
        """
        import json
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"silent_bugs_summary_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # 构建摘要数据
        summary_data = {
            "generated_at": datetime.now().isoformat(),
            "total_silent_bugs": len(silent_bugs),
            "issues": []
        }
        
        for issue, result in silent_bugs:
            issue_data = {
                "issue": issue.to_dict(),
                "analysis": result.to_dict()
            }
            summary_data["issues"].append(issue_data)
            
        # 写入JSON文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
            
        print(f"JSON摘要已生成: {filepath}")
        return str(filepath)
