#!/usr/bin/env python3
"""
DeepSeek/OpenAI兼容客户端单元测试
"""

import unittest
from unittest.mock import MagicMock
import requests
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.llm.deepseek_client import DeepSeekClient


class TestDeepSeekClient(unittest.TestCase):
    """DeepSeekClient测试类"""

    def test_url_normalization_with_v1(self):
        client = DeepSeekClient(api_key="k", base_url="http://example.com/v1")
        self.assertEqual(
            client._get_chat_completions_url(),
            "http://example.com/v1/chat/completions",
        )

    def test_url_normalization_without_v1(self):
        client = DeepSeekClient(api_key="k", base_url="http://example.com")
        self.assertEqual(
            client._get_chat_completions_url(),
            "http://example.com/v1/chat/completions",
        )

    def test_disable_env_proxy_by_default(self):
        client = DeepSeekClient(api_key="k")
        self.assertFalse(client.session.trust_env)

    def test_enable_env_proxy_when_configured(self):
        client = DeepSeekClient(api_key="k", use_env_proxy=True)
        self.assertTrue(client.session.trust_env)

    def test_retry_on_timeout_then_success(self):
        client = DeepSeekClient(api_key="k", max_retries=1, retry_backoff=0)

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": '{"is_silent_bug": false, "confidence": 0.1, "root_cause": "其他", "summary": "ok", "affected_software": [], "defense_mechanisms": [], "severity": "低", "recommendations": []}'
                    }
                }
            ]
        }

        client.session.post = MagicMock(
            side_effect=[requests.exceptions.Timeout("timeout"), mock_response]
        )

        result = client.analyze_issue("content", "title")
        self.assertIn("is_silent_bug", result)
        self.assertEqual(client.session.post.call_count, 2)


if __name__ == "__main__":
    unittest.main()
