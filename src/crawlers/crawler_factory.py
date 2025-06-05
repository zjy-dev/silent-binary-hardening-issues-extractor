"""
爬虫工厂 - 创建不同类型的爬虫
"""

from typing import List, Dict, Any
from src.core.base_crawler import BaseCrawler
from src.crawlers.lore_kernel_crawler import LoreKernelCrawler


class CrawlerFactory:
    """爬虫工厂类"""
    
    @staticmethod
    def create_crawler(crawler_type: str, keywords: List[str], year: int = 2025) -> BaseCrawler:
        """
        创建指定类型的爬虫
        
        Args:
            crawler_type: 爬虫类型
            keywords: 关键词列表
            year: 爬取年份
            
        Returns:
            爬虫实例
        """
        crawler_type = crawler_type.lower()
        
        if crawler_type == "lore_kernel":
            return LoreKernelCrawler(keywords, year)
        else:
            raise ValueError(f"不支持的爬虫类型: {crawler_type}")
            
    @staticmethod
    def get_available_crawlers() -> List[str]:
        """
        获取可用的爬虫类型列表
        
        Returns:
            爬虫类型列表
        """
        return ["lore_kernel"]
        
    @staticmethod
    def create_all_crawlers(keywords: List[str], year: int = 2025) -> List[BaseCrawler]:
        """
        创建所有可用的爬虫
        
        Args:
            keywords: 关键词列表
            year: 爬取年份
            
        Returns:
            爬虫实例列表
        """
        crawlers = []
        
        for crawler_type in CrawlerFactory.get_available_crawlers():
            try:
                crawler = CrawlerFactory.create_crawler(crawler_type, keywords, year)
                crawlers.append(crawler)
            except Exception as e:
                print(f"创建爬虫 {crawler_type} 失败: {e}")
                
        return crawlers
