"""
基础爬虫抽象类 - 定义爬虫接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class BaseCrawler(ABC):
    """爬虫基类，定义所有爬虫的通用接口"""
    
    def __init__(self, name: str, base_url: str, keywords: List[str], year: int = 2025):
        """
        初始化爬虫
        
        Args:
            name: 爬虫名称
            base_url: 基础URL
            keywords: 关键词列表
            year: 爬取年份，默认2025
        """
        self.name = name
        self.base_url = base_url
        self.keywords = keywords
        self.year = year
        
    @abstractmethod
    def crawl(self, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        爬取数据的主要方法
        
        Args:
            max_pages: 最大页数限制
            
        Returns:
            包含爬取数据的字典列表
        """
        pass
        
    @abstractmethod
    def parse_page(self, html_content: str) -> List[Dict[str, Any]]:
        """
        解析页面内容
        
        Args:
            html_content: HTML内容
            
        Returns:
            解析后的数据列表
        """
        pass
        
    @abstractmethod
    def build_search_url(self, page: int = 0) -> str:
        """
        构建搜索URL
        
        Args:
            page: 页码
            
        Returns:
            搜索URL
        """
        pass
        
    def filter_by_keywords(self, content: str) -> bool:
        """
        根据关键词过滤内容
        
        Args:
            content: 要检查的内容
            
        Returns:
            是否包含关键词
        """
        if not content:
            return False
        content_lower = content.lower()
        return any(keyword.lower() in content_lower for keyword in self.keywords)
        
    def filter_by_year(self, date_str: str) -> bool:
        """
        根据年份过滤
        
        Args:
            date_str: 日期字符串
            
        Returns:
            是否符合年份要求
        """
        try:
            # 尝试解析常见的日期格式
            for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d %b %Y', '%b %d, %Y']:
                try:
                    date_obj = datetime.strptime(date_str.strip(), fmt)
                    return date_obj.year == self.year
                except ValueError:
                    continue
            return False
        except Exception:
            return False
