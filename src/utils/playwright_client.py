"""
基于Playwright的HTTP客户端，用于处理JavaScript渲染和反爬虫保护
"""

import asyncio
import time
from typing import Optional, Dict, Any, List
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from playwright.async_api import TimeoutError as PlaywrightTimeoutError


class PlaywrightClient:
    """基于Playwright的HTTP客户端，支持JavaScript执行和反爬虫保护绕过"""
    
    def __init__(self, 
                 timeout: int = 30000,  # Playwright使用毫秒
                 delay: float = 1.0,
                 headless: bool = True,
                 max_retries: int = 3):
        """
        初始化Playwright客户端
        
        Args:
            timeout: 页面加载超时时间（毫秒）
            delay: 请求间延迟（秒）
            headless: 是否无头模式
            max_retries: 最大重试次数
        """
        self.timeout = timeout
        self.delay = delay
        self.headless = headless
        self.max_retries = max_retries
        
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self._initialized = False
        
    async def _initialize(self):
        """初始化Playwright浏览器"""
        if self._initialized:
            return
            
        self.playwright = await async_playwright().start()
        
        # 启动Chromium浏览器
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--disable-extensions',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
            ]
        )
        
        # 创建浏览器上下文，模拟真实浏览器
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
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
            }
        )
        
        # 设置JavaScript以隐藏自动化特征
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // 删除window.chrome.runtime
            delete window.chrome;
            
            // 重写languages属性
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en', 'zh-CN', 'zh'],
            });
            
            // 重写plugins长度
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3],
            });
        """)
        
        self._initialized = True
        
    async def get(self, url: str, wait_for: Optional[str] = None) -> Optional[str]:
        """
        发送GET请求并获取页面内容
        
        Args:
            url: 请求URL
            wait_for: 等待的元素选择器或网络状态
            
        Returns:
            页面HTML内容，失败返回None
        """
        await self._initialize()
        
        retries = 0
        while retries < self.max_retries:
            page: Optional[Page] = None
            try:
                page = await self.context.new_page()
                
                # 设置超时
                page.set_default_timeout(self.timeout)
                
                # 监听控制台输出（用于调试）
                page.on('console', lambda msg: print(f"Console: {msg.text}"))
                
                print(f"正在访问: {url}")
                
                # 导航到页面
                response = await page.goto(url, wait_until='networkidle')
                
                if response and response.status >= 400:
                    print(f"HTTP错误: {response.status}")
                    if retries < self.max_retries - 1:
                        retries += 1
                        await page.close()
                        await asyncio.sleep(2 ** retries)  # 指数退避
                        continue
                    return None
                
                # 等待特定元素或条件
                if wait_for:
                    if wait_for in ['load', 'domcontentloaded', 'networkidle']:
                        await page.wait_for_load_state(wait_for)
                    else:
                        # 假设是CSS选择器
                        await page.wait_for_selector(wait_for, timeout=10000)
                
                # 检查是否遇到反爬虫保护
                await self._handle_anti_crawl_protection(page)
                
                # 获取页面内容
                content = await page.content()
                
                await page.close()
                
                # 延迟以避免过快请求
                if self.delay > 0:
                    await asyncio.sleep(self.delay)
                
                return content
                
            except PlaywrightTimeoutError:
                print(f"页面加载超时: {url}")
                if page:
                    await page.close()
                if retries < self.max_retries - 1:
                    retries += 1
                    await asyncio.sleep(2 ** retries)
                    continue
                return None
                
            except Exception as e:
                print(f"请求失败 {url}: {e}")
                if page:
                    await page.close()
                if retries < self.max_retries - 1:
                    retries += 1
                    await asyncio.sleep(2 ** retries)
                    continue
                return None
        
        return None
        
    async def _handle_anti_crawl_protection(self, page: Page):
        """
        处理常见的反爬虫保护机制
        
        Args:
            page: Playwright页面对象
        """
        try:
            # 检查是否有Anubis Proof-of-Work保护
            anubis_script = await page.query_selector('script[src*="anubis"]')
            if anubis_script:
                print("检测到Anubis反爬虫保护，等待解决...")
                # 等待最多30秒让Anubis完成验证
                await page.wait_for_timeout(30000)
                return
                
            # 检查Cloudflare保护
            cf_challenge = await page.query_selector('#cf-challenge-running')
            if cf_challenge:
                print("检测到Cloudflare保护，等待验证完成...")
                await page.wait_for_selector('#cf-challenge-running', state='detached', timeout=30000)
                return
                
            # 检查其他常见的验证元素
            challenge_selectors = [
                '[data-challenge]',
                '.challenge-form',
                '#challenge',
                '.captcha',
                '.verification'
            ]
            
            for selector in challenge_selectors:
                element = await page.query_selector(selector)
                if element:
                    print(f"检测到验证元素: {selector}")
                    await page.wait_for_timeout(5000)  # 等待5秒
                    break
                    
        except Exception as e:
            print(f"处理反爬虫保护时出错: {e}")
            
    async def get_multiple(self, urls: List[str]) -> List[Optional[str]]:
        """
        并发获取多个URL的内容
        
        Args:
            urls: URL列表
            
        Returns:
            对应的HTML内容列表
        """
        await self._initialize()
        
        tasks = [self.get(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                print(f"并发请求异常: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
                
        return processed_results
        
    async def close(self):
        """关闭浏览器和Playwright"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self._initialized = False


class SyncPlaywrightClient:
    """同步版本的Playwright客户端，封装异步操作"""
    
    def __init__(self, **kwargs):
        self.async_client = PlaywrightClient(**kwargs)
        self._loop = None
        
    def _get_event_loop(self):
        """获取或创建事件循环"""
        try:
            # 尝试获取当前事件循环
            loop = asyncio.get_running_loop()
            return loop
        except RuntimeError:
            # 如果没有运行的事件循环，创建新的
            if self._loop is None or self._loop.is_closed():
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
            return self._loop
            
    def get(self, url: str, wait_for: Optional[str] = None) -> Optional[str]:
        """同步版本的get方法"""
        loop = self._get_event_loop()
        try:
            return loop.run_until_complete(self.async_client.get(url, wait_for))
        except RuntimeError as e:
            if "This event loop is already running" in str(e):
                # 如果在已运行的事件循环中，使用新的事件循环
                import threading
                result = [None]
                exception = [None]
                
                def run_in_thread():
                    try:
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        result[0] = new_loop.run_until_complete(
                            PlaywrightClient(**self.async_client.__dict__).get(url, wait_for)
                        )
                        new_loop.close()
                    except Exception as e:
                        exception[0] = e
                
                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()
                
                if exception[0]:
                    raise exception[0]
                return result[0]
            else:
                raise
                
    def get_multiple(self, urls: List[str]) -> List[Optional[str]]:
        """同步版本的批量获取方法"""
        loop = self._get_event_loop()
        return loop.run_until_complete(self.async_client.get_multiple(urls))
        
    def close(self):
        """关闭客户端"""
        loop = self._get_event_loop()
        loop.run_until_complete(self.async_client.close())
        if self._loop and not self._loop.is_running():
            self._loop.close()
