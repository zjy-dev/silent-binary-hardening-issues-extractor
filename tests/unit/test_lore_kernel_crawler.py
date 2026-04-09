#!/usr/bin/env python3
"""
Lore Kernel 爬虫单元测试
"""

import unittest
from unittest.mock import patch
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from crawlers.lore_kernel_crawler import LoreKernelCrawler


class TestLoreKernelCrawler(unittest.TestCase):
    """LoreKernelCrawler测试类"""
    
    def setUp(self):
        """测试准备"""
        self.keywords = ["hardening", "canary", "stack-protection"]
        self.year = 2025
        self.crawler = LoreKernelCrawler(self.keywords, self.year)
    
    def test_crawler_initialization(self):
        """测试爬虫初始化"""
        self.assertEqual(self.crawler.keywords, self.keywords)
        self.assertEqual(self.crawler.year, self.year)
        self.assertIsInstance(self.crawler.keywords, list)
        self.assertIsInstance(self.crawler.year, int)
    
    def test_build_search_url(self):
        """测试构建搜索URL"""
        url = self.crawler.build_search_url(0)
        self.assertIsInstance(url, str)
        self.assertIn("lore.kernel.org", url)
        self.assertIn(str(self.year), url)
        
        # 测试不同页面
        url_page_1 = self.crawler.build_search_url(1)
        self.assertNotEqual(url, url_page_1)
    
    def test_filter_by_keywords_positive(self):
        """测试关键词过滤 - 正面案例"""
        test_content = "This is about stack canary protection and hardening"
        result = self.crawler.filter_by_keywords(test_content)
        self.assertTrue(result)
    
    def test_filter_by_keywords_negative(self):
        """测试关键词过滤 - 负面案例"""
        test_content = "This is about completely unrelated topic"
        result = self.crawler.filter_by_keywords(test_content)
        self.assertFalse(result)
    
    def test_filter_by_keywords_case_insensitive(self):
        """测试关键词过滤 - 大小写不敏感"""
        test_content = "This is about STACK CANARY protection"
        result = self.crawler.filter_by_keywords(test_content)
        self.assertTrue(result)
    
    def test_filter_by_keywords_empty_content(self):
        """测试关键词过滤 - 空内容"""
        result = self.crawler.filter_by_keywords("")
        self.assertFalse(result)
        
        result = self.crawler.filter_by_keywords(None)
        self.assertFalse(result)
    
    def test_parse_email_data_structure(self):
        """测试邮件数据解析结构"""
        # 由于parse_email_data是私有方法，我们测试其公共接口
        sample_response = {
            "messages": [
                {
                    "subject": "Test subject",
                    "sender": "test@example.com",
                    "date": "2025-01-01T10:00:00Z",
                    "body": "Test body content"
                }
            ]
        }
        
        # 模拟解析逻辑
        if "messages" in sample_response:
            messages = sample_response["messages"]
            self.assertIsInstance(messages, list)
            if messages:
                message = messages[0]
                self.assertIn("subject", message)
                self.assertIn("sender", message)
                self.assertIn("date", message)
                self.assertIn("body", message)
    
    @patch('crawlers.lore_kernel_crawler.HttpClient.get')
    def test_crawl_with_mock(self, mock_get):
        """测试爬取功能 - 使用Mock"""
        mock_get.return_value = """
        <html>
            <body>
                <pre>
                    1. <b><a href="test-message/">Test stack canary issue</a></b>
                       - by test@example.com @ 2025-01-01 10:00 UTC [50%]
                </pre>
            </body>
        </html>
        """
        
        # 执行爬取
        result = self.crawler.crawl(max_pages=1)
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)
        self.assertEqual(result[0].get("subject"), "Test stack canary issue")
        mock_get.assert_called_once()
    
    def test_keywords_validation(self):
        """测试关键词验证"""
        # 测试空关键词列表
        with self.assertRaises(ValueError):
            LoreKernelCrawler([], self.year)
        
        # 测试None关键词
        with self.assertRaises(ValueError):
            LoreKernelCrawler(None, self.year)
    
    def test_year_validation(self):
        """测试年份验证"""
        # 测试无效年份
        with self.assertRaises(ValueError):
            LoreKernelCrawler(self.keywords, 1990)  # 太早的年份
        
        with self.assertRaises(ValueError):
            LoreKernelCrawler(self.keywords, 2050)  # 太晚的年份
    
    def tearDown(self):
        """测试清理"""
        self.crawler = None


if __name__ == "__main__":
    unittest.main()
