"""
DeepSeek LLM客户端实现
"""

import requests
import json
from typing import Dict, Any, Optional

from src.llm.base_llm import BaseLLM


class DeepSeekClient(BaseLLM):
    """DeepSeek LLM客户端"""
    
    def __init__(self, api_key: str, model: str = "deepseek-chat", 
                 base_url: str = "https://api.deepseek.com"):
        """
        初始化DeepSeek客户端
        
        Args:
            api_key: DeepSeek API密钥
            model: 模型名称
            base_url: API基础URL
        """
        super().__init__(api_key, model, base_url)
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def analyze_issue(self, issue_content: str, issue_title: str = "") -> Dict[str, Any]:
        """
        使用DeepSeek分析安全问题
        
        Args:
            issue_content: 问题内容
            issue_title: 问题标题
            
        Returns:
            分析结果字典
        """
        try:
            prompt = self.create_analysis_prompt(issue_content, issue_title)
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return self.parse_analysis_result(content)
            else:
                return self._get_default_result("API响应格式错误")
                
        except requests.exceptions.RequestException as e:
            print(f"DeepSeek API请求失败: {e}")
            return self._get_default_result(f"API请求失败: {e}")
        except Exception as e:
            print(f"DeepSeek分析过程出错: {e}")
            return self._get_default_result(f"分析过程出错: {e}")
