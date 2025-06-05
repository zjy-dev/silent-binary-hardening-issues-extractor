"""
HTTP客户端工具 - 支持requests和Playwright两种模式
"""

import time
import requests
from typing import Optional, Literal
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from .playwright_client import SyncPlaywrightClient
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    SyncPlaywrightClient = None


class HttpClient:
    """HTTP请求客户端，支持requests和Playwright两种模式"""
    
    def __init__(self, 
                 timeout: int = 30, 
                 max_retries: int = 3, 
                 delay: float = 1.0,
                 mode: Literal["requests", "playwright"] = "requests",
                 headless: bool = True):
        """
        初始化HTTP客户端
        
        Args:
            timeout: 请求超时时间
            max_retries: 最大重试次数
            delay: 请求间延迟
            mode: 客户端模式，"requests"或"playwright"
            headless: 仅Playwright模式：是否无头模式
        """
        self.timeout = timeout
        self.delay = delay
        self.mode = mode
        self.headless = headless
        
        # 初始化对应的客户端
        if mode == "playwright":
            if not PLAYWRIGHT_AVAILABLE:
                raise ImportError("Playwright未安装，请运行: pip install playwright")
            self.playwright_client = SyncPlaywrightClient(
                timeout=timeout * 1000,  # 转换为毫秒
                delay=delay,
                headless=headless,
                max_retries=max_retries
            )
            self.session = None
        else:
            self.playwright_client = None
            self._init_requests_session(max_retries)
            
    def _init_requests_session(self, max_retries: int):
        """初始化requests session"""
        # 创建session
        self.session = requests.Session()
        
        # 设置更完整的浏览器Headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        })
        
        # 配置重试策略
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
    def get(self, url: str, wait_for: Optional[str] = None) -> Optional[str]:
        """
        发送GET请求
        
        Args:
            url: 请求URL
            wait_for: 仅Playwright模式：等待的元素选择器或网络状态
            
        Returns:
            响应内容，失败返回None
        """
        if self.mode == "playwright":
            return self.playwright_client.get(url, wait_for)
        else:
            return self._requests_get(url)
            
    def _requests_get(self, url: str) -> Optional[str]:
        """使用requests发送GET请求"""
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # 延迟以避免过快请求
            time.sleep(self.delay)
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"请求失败 {url}: {e}")
            return None
            
    def close(self):
        """关闭客户端"""
        if self.mode == "playwright" and self.playwright_client:
            self.playwright_client.close()
        elif self.session:
            self.session.close()
            
    def switch_mode(self, mode: Literal["requests", "playwright"], **kwargs):
        """
        切换客户端模式
        
        Args:
            mode: 新的客户端模式
            **kwargs: 新模式的参数
        """
        # 关闭当前客户端
        self.close()
        
        # 更新模式
        self.mode = mode
        
        # 重新初始化
        if mode == "playwright":
            if not PLAYWRIGHT_AVAILABLE:
                raise ImportError("Playwright未安装，请运行: pip install playwright")
            self.playwright_client = SyncPlaywrightClient(
                timeout=self.timeout * 1000,
                delay=self.delay,
                headless=kwargs.get('headless', self.headless),
                max_retries=kwargs.get('max_retries', 3)
            )
            self.session = None
        else:
            self.playwright_client = None
            self._init_requests_session(kwargs.get('max_retries', 3))
