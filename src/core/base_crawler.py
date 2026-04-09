"""
基础爬虫抽象类 - 定义爬虫接口
"""

import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class BaseCrawler(ABC):
    """爬虫基类，定义所有爬虫的通用接口"""
    
    def __init__(self, name: str, base_url: str, keywords: List[str], year: int | List[int] = 2025):
        """
        初始化爬虫
        
        Args:
            name: 爬虫名称
            base_url: 基础URL
            keywords: 关键词列表
            year: 爬取年份，支持单年或多年
        """
        self.name = name
        self.base_url = base_url
        self.keywords = self._validate_keywords(keywords)
        self.years = self._normalize_years(year)
        self.year = self.years[0]  # 兼容旧逻辑
        
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
        if not date_str:
            return False

        try:
            normalized_date = re.sub(r'\s+', ' ', date_str.strip())

            # 尝试解析常见日期格式（包含 lore 的 UTC 格式）
            for fmt in [
                '%Y-%m-%d %H:%M UTC',
                '%Y-%m-%d',
                '%Y/%m/%d',
                '%d %b %Y',
                '%b %d, %Y',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%S%z',
            ]:
                try:
                    date_obj = datetime.strptime(normalized_date, fmt)
                    return date_obj.year in self.years
                except ValueError:
                    continue

            # ISO时间戳（带Z）
            if normalized_date.endswith('Z'):
                iso_date = normalized_date.replace('Z', '+00:00')
                date_obj = datetime.fromisoformat(iso_date)
                return date_obj.year in self.years

            # 最后回退：直接提取字符串里的年份
            year_match = re.search(r'(19|20)\d{2}', normalized_date)
            if year_match:
                return int(year_match.group(0)) in self.years

            return False
        except Exception:
            return False

    def _validate_keywords(self, keywords: List[str]) -> List[str]:
        """验证关键词配置"""
        if not isinstance(keywords, list) or not keywords:
            raise ValueError("关键词列表不能为空")

        normalized_keywords = [str(keyword).strip() for keyword in keywords if str(keyword).strip()]
        if not normalized_keywords:
            raise ValueError("关键词列表不能为空")

        return normalized_keywords

    def _normalize_years(self, year: int | List[int]) -> List[int]:
        """将年份参数规范化为列表并做范围校验"""
        if isinstance(year, int):
            year_list = [year]
        elif isinstance(year, list) and year:
            try:
                year_list = [int(item) for item in year]
            except (TypeError, ValueError):
                raise ValueError("年份配置必须为整数或整数列表")
        else:
            raise ValueError("年份配置必须为整数或非空整数列表")

        current_year = datetime.now().year
        min_year = 2000
        max_year = current_year + 5

        for item in year_list:
            if item < min_year or item > max_year:
                raise ValueError(f"年份超出有效范围: {item} (允许 {min_year}-{max_year})")

        unique_years: List[int] = []
        for item in year_list:
            if item not in unique_years:
                unique_years.append(item)

        return unique_years
