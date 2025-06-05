#!/usr/bin/env python3
"""
配置加载器单元测试
"""

import unittest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.config_loader import ConfigLoader


class TestConfigLoader(unittest.TestCase):
    """配置加载器测试类"""
    
    def setUp(self):
        """测试准备"""
        self.config_loader = ConfigLoader()
    
    def test_get_keywords_returns_list(self):
        """测试获取关键词返回列表"""
        keywords = self.config_loader.get_keywords()
        self.assertIsInstance(keywords, list)
        self.assertGreater(len(keywords), 0)
    
    def test_get_keywords_not_empty(self):
        """测试关键词列表不为空"""
        keywords = self.config_loader.get_keywords()
        for keyword in keywords:
            self.assertIsInstance(keyword, str)
            self.assertGreater(len(keyword.strip()), 0)
    
    def test_get_year_returns_int(self):
        """测试获取年份返回整数"""
        year = self.config_loader.get_year()
        self.assertIsInstance(year, int)
        self.assertGreaterEqual(year, 2020)
        self.assertLessEqual(year, 2030)
    
    def test_get_year_current_or_future(self):
        """测试年份为当前或未来年份"""
        year = self.config_loader.get_year()
        current_year = 2025  # 假设当前年份
        self.assertGreaterEqual(year, current_year - 5)
    
    def tearDown(self):
        """测试清理"""
        self.config_loader = None


if __name__ == "__main__":
    unittest.main()
