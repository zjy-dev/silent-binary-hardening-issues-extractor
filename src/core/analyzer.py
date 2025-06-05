"""
分析器 - 使用LLM分析爬取的数据
"""

from typing import List, Dict, Any
from src.models.issue import Issue, AnalysisResult
from src.llm.base_llm import BaseLLM
from src.llm.deepseek_client import DeepSeekClient


class Analyzer:
    """数据分析器，使用LLM分析爬取的安全问题"""
    
    def __init__(self, llm_client: BaseLLM):
        """
        初始化分析器
        
        Args:
            llm_client: LLM客户端实例
        """
        self.llm_client = llm_client
        
    def analyze_issues(self, issues: List[Issue]) -> List[tuple[Issue, AnalysisResult]]:
        """
        批量分析安全问题
        
        Args:
            issues: 问题列表
            
        Returns:
            (问题, 分析结果) 元组列表
        """
        results = []
        
        print(f"开始分析 {len(issues)} 个问题...")
        
        for i, issue in enumerate(issues, 1):
            print(f"正在分析第 {i}/{len(issues)} 个问题: {issue.title[:50]}...")
            
            try:
                analysis_dict = self.llm_client.analyze_issue(issue.content, issue.title)
                analysis_result = AnalysisResult(**analysis_dict)
                results.append((issue, analysis_result))
                
            except Exception as e:
                print(f"分析问题 {i} 时出错: {e}")
                # 创建错误分析结果
                error_result = AnalysisResult(
                    is_silent_bug=False,
                    confidence=0.0,
                    root_cause="分析失败",
                    summary=f"分析失败: {e}",
                    affected_software=[],
                    defense_mechanisms=[],
                    severity="未知",
                    recommendations=[]
                )
                results.append((issue, error_result))
                
        print(f"分析完成，共处理 {len(results)} 个问题")
        return results
        
    def filter_silent_bugs(self, analyzed_results: List[tuple[Issue, AnalysisResult]], 
                         min_confidence: float = 0.5) -> List[tuple[Issue, AnalysisResult]]:
        """
        过滤出Silent Bug
        
        Args:
            analyzed_results: 分析结果列表
            min_confidence: 最小置信度阈值
            
        Returns:
            过滤后的Silent Bug列表
        """
        silent_bugs = []
        
        for issue, result in analyzed_results:
            if result.is_silent_bug and result.confidence >= min_confidence:
                silent_bugs.append((issue, result))
                
        print(f"找到 {len(silent_bugs)} 个Silent Bug (置信度 >= {min_confidence})")
        return silent_bugs
        
    @staticmethod
    def create_analyzer_from_config(llm_config: Dict[str, Any]) -> 'Analyzer':
        """
        根据配置创建分析器
        
        Args:
            llm_config: LLM配置字典
            
        Returns:
            分析器实例
        """
        provider = llm_config.get('provider', 'deepseek').lower()
        
        if provider == 'deepseek':
            llm_client = DeepSeekClient(
                api_key=llm_config.get('api_key', ''),
                model=llm_config.get('model', 'deepseek-chat'),
                base_url=llm_config.get('base_url', 'https://api.deepseek.com')
            )
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")
            
        return Analyzer(llm_client)
