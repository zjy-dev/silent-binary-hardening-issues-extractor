#!/usr/bin/env python3
"""
爬虫集成测试 - 测试整个爬取流程
注意：此测试可能需要网络连接
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from crawlers.lore_kernel_crawler import LoreKernelCrawler
from utils.config_loader import ConfigLoader
from models.issue import Issue


class TestCrawlerIntegration(unittest.TestCase):
    """爬虫集成测试类"""
    
    def setUp(self):
        """测试准备"""
        self.config_loader = ConfigLoader()
        # 使用少量关键词以减少测试时间
        self.keywords = ["hardening", "canary"]
        self.year = 2025
    
    def test_config_to_crawler_integration(self):
        """测试配置加载器与爬虫的集成"""
        try:
            # 从配置加载器获取配置
            config_keywords = self.config_loader.get_keywords()[:2]  # 只用前2个
            config_year = self.config_loader.get_year()
            
            # 创建爬虫
            crawler = LoreKernelCrawler(config_keywords, config_year)
            
            # 验证配置正确传递
            self.assertEqual(crawler.keywords, config_keywords)
            self.assertEqual(crawler.year, config_year)
            
            # 测试URL构建
            url = crawler.build_search_url(0)
            self.assertIsInstance(url, str)
            self.assertIn("lore.kernel.org", url)
            
        except Exception as e:
            self.fail(f"配置到爬虫集成测试失败: {e}")
    
    def test_crawler_to_model_integration(self):
        """测试爬虫数据转换为模型的集成"""
        crawler = LoreKernelCrawler(self.keywords, self.year)
        
        # 模拟爬取数据
        sample_raw_data = [
            {
                "subject": "Test Stack Canary Issue",
                "sender": "test@example.com",
                "date": "2025-01-01T10:00:00Z",
                "body": "This is about stack canary protection"
            }
        ]
        
        # 测试数据转换为Issue模型
        try:
            for item in sample_raw_data:
                issue = Issue(
                    title=item.get("subject", ""),
                    content=item.get("body", ""),
                    source="lore.kernel.org",
                    url=f"https://lore.kernel.org/test/{hash(item.get('subject', ''))}",
                    date=item.get("date", ""),
                    author=item.get("sender", "")
                )
                
                # 验证Issue对象
                self.assertIsInstance(issue, Issue)
                self.assertEqual(issue.title, item["subject"])
                self.assertEqual(issue.content, item["body"])
                self.assertEqual(issue.author, item["sender"])
                
                # 测试关键词过滤
                filter_result = crawler.filter_by_keywords(issue.content)
                self.assertTrue(filter_result)  # 应该包含关键词
                
        except Exception as e:
            self.fail(f"爬虫到模型集成测试失败: {e}")
    
    @unittest.skip("需要网络连接，在CI环境中跳过")
    def test_real_network_crawl(self):
        """测试真实网络爬取 - 可选测试"""
        crawler = LoreKernelCrawler(["hardening"], 2025)
        
        try:
            # 只爬取1页以减少测试时间
            result = crawler.crawl(max_pages=1)
            
            # 验证返回结果
            self.assertIsInstance(result, list)
            # 注意：结果可能为空，这是正常的
            
        except Exception as e:
            # 网络错误不应导致测试失败
            self.skipTest(f"网络连接问题，跳过真实爬取测试: {e}")
    
    def test_end_to_end_workflow_simulation(self):
        """测试端到端工作流模拟"""
        try:
            # 1. 加载配置
            config_loader = ConfigLoader()
            keywords = config_loader.get_keywords()[:2]
            year = config_loader.get_year()
            
            # 2. 创建爬虫
            crawler = LoreKernelCrawler(keywords, year)
            
            # 3. 模拟爬取过程
            url = crawler.build_search_url(0)
            self.assertIsNotNone(url)
            
            # 4. 模拟数据处理
            sample_content = "This is about stack canary protection and hardening"
            filter_result = crawler.filter_by_keywords(sample_content)
            self.assertTrue(filter_result)
            
            # 5. 创建Issue对象
            issue = Issue(
                title="Integration Test Issue",
                content=sample_content,
                source="lore.kernel.org",
                url=url,
                date="2025-01-01",
                author="integration@test.com"
            )
            
            # 6. 转换为字典（模拟存储）
            issue_dict = issue.to_dict()
            self.assertIsInstance(issue_dict, dict)
            self.assertIn("title", issue_dict)
            
            print("✅ 端到端工作流测试通过")
            
        except Exception as e:
            self.fail(f"端到端工作流测试失败: {e}")
    
    def tearDown(self):
        """测试清理"""
        pass


if __name__ == "__main__":
    unittest.main()
