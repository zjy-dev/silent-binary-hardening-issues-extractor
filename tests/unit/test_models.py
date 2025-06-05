#!/usr/bin/env python3
"""
数据模型单元测试
"""

import unittest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from models.issue import Issue, AnalysisResult


class TestIssue(unittest.TestCase):
    """Issue模型测试类"""
    
    def setUp(self):
        """测试准备"""
        self.sample_data = {
            "title": "Test Stack Canary Issue",
            "content": "This is a test content about stack canary protection",
            "source": "lore.kernel.org",
            "url": "https://lore.kernel.org/test/123456",
            "date": "2025-01-01",
            "author": "test@example.com"
        }
    
    def test_issue_creation(self):
        """测试Issue对象创建"""
        issue = Issue(**self.sample_data)
        self.assertEqual(issue.title, self.sample_data["title"])
        self.assertEqual(issue.content, self.sample_data["content"])
        self.assertEqual(issue.source, self.sample_data["source"])
        self.assertEqual(issue.url, self.sample_data["url"])
        self.assertEqual(issue.date, self.sample_data["date"])
        self.assertEqual(issue.author, self.sample_data["author"])
    
    def test_issue_to_dict(self):
        """测试Issue转换为字典"""
        issue = Issue(**self.sample_data)
        issue_dict = issue.to_dict()
        
        self.assertIsInstance(issue_dict, dict)
        for key, value in self.sample_data.items():
            self.assertEqual(issue_dict[key], value)
    
    def test_issue_required_fields(self):
        """测试Issue必填字段"""
        # 测试缺少必填字段时的行为
        with self.assertRaises(TypeError):
            Issue()  # 缺少必需参数
    
    def test_issue_string_representation(self):
        """测试Issue字符串表示"""
        issue = Issue(**self.sample_data)
        str_repr = str(issue)
        self.assertIn(self.sample_data["title"], str_repr)


class TestAnalysisResult(unittest.TestCase):
    """AnalysisResult模型测试类"""
    
    def setUp(self):
        """测试准备"""
        self.sample_data = {
            "is_silent_bug": True,
            "confidence": 0.9,
            "root_cause": "配置缺失",
            "summary": "Stack canary 未启用"
        }
    
    def test_analysis_result_creation(self):
        """测试AnalysisResult对象创建"""
        analysis = AnalysisResult(**self.sample_data)
        self.assertEqual(analysis.is_silent_bug, self.sample_data["is_silent_bug"])
        self.assertEqual(analysis.confidence, self.sample_data["confidence"])
        self.assertEqual(analysis.root_cause, self.sample_data["root_cause"])
        self.assertEqual(analysis.summary, self.sample_data["summary"])
    
    def test_analysis_result_to_dict(self):
        """测试AnalysisResult转换为字典"""
        analysis = AnalysisResult(**self.sample_data)
        analysis_dict = analysis.to_dict()
        
        self.assertIsInstance(analysis_dict, dict)
        for key, value in self.sample_data.items():
            self.assertEqual(analysis_dict[key], value)
    
    def test_confidence_range(self):
        """测试置信度范围"""
        # 测试有效的置信度值
        analysis = AnalysisResult(
            is_silent_bug=True,
            confidence=0.5,
            root_cause="测试",
            summary="测试"
        )
        self.assertGreaterEqual(analysis.confidence, 0.0)
        self.assertLessEqual(analysis.confidence, 1.0)
    
    def test_boolean_is_silent_bug(self):
        """测试is_silent_bug为布尔值"""
        analysis = AnalysisResult(**self.sample_data)
        self.assertIsInstance(analysis.is_silent_bug, bool)
    
    def tearDown(self):
        """测试清理"""
        pass


if __name__ == "__main__":
    unittest.main()
