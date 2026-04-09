"""
DeepSeek LLM客户端实现
"""

import time
import requests
from typing import Dict, Any

from src.llm.base_llm import BaseLLM


class DeepSeekClient(BaseLLM):
    """DeepSeek LLM客户端"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com",
        timeout: int = 120,
        max_retries: int = 2,
        retry_backoff: float = 1.0,
        use_env_proxy: bool = False,
    ):
        """
        初始化DeepSeek客户端
        
        Args:
            api_key: DeepSeek API密钥
            model: 模型名称
            base_url: API基础URL
            timeout: 读取超时时间（秒）
            max_retries: 失败重试次数
            retry_backoff: 指数退避基础秒数
            use_env_proxy: 是否使用环境变量中的代理
        """
        super().__init__(api_key, model, base_url)
        self.timeout = max(1, int(timeout))
        self.max_retries = max(0, int(max_retries))
        self.retry_backoff = max(0.0, float(retry_backoff))
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.trust_env = bool(use_env_proxy)

    def _get_chat_completions_url(self) -> str:
        """构建兼容OpenAI风格的chat completions接口URL"""
        normalized_base_url = (self.base_url or "https://api.deepseek.com").rstrip("/")

        if normalized_base_url.endswith("/chat/completions"):
            return normalized_base_url

        if normalized_base_url.endswith("/v1"):
            return f"{normalized_base_url}/chat/completions"

        return f"{normalized_base_url}/v1/chat/completions"

    def _request_chat_completions(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """带重试的chat completions请求"""
        endpoint = self._get_chat_completions_url()
        total_attempts = self.max_retries + 1

        for attempt in range(1, total_attempts + 1):
            try:
                response = self.session.post(
                    endpoint,
                    headers=self.headers,
                    json=payload,
                    timeout=(10, self.timeout),
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                status_code = e.response.status_code if e.response is not None else None
                is_retriable = status_code in {408, 429, 500, 502, 503, 504}
                if attempt < total_attempts and is_retriable:
                    wait_seconds = self.retry_backoff * (2 ** (attempt - 1))
                    print(f"DeepSeek API请求返回 {status_code}，{wait_seconds:.1f}s 后重试...")
                    if wait_seconds > 0:
                        time.sleep(wait_seconds)
                    continue
                raise
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                if attempt < total_attempts:
                    wait_seconds = self.retry_backoff * (2 ** (attempt - 1))
                    print(f"DeepSeek API请求第 {attempt}/{total_attempts} 次失败，{wait_seconds:.1f}s 后重试: {e}")
                    if wait_seconds > 0:
                        time.sleep(wait_seconds)
                    continue
                raise
        
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

            result = self._request_chat_completions(payload)
            
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
