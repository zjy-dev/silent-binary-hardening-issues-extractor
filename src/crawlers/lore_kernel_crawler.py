"""
Lore Kernel 爬虫实现
"""

import re
import time
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode, quote_plus
from bs4 import BeautifulSoup

from src.core.base_crawler import BaseCrawler
from src.utils.http_client import HttpClient


class LoreKernelCrawler(BaseCrawler):
    """Lore Kernel 邮件列表爬虫"""
    
    def __init__(self, keywords: List[str], year: int = 2025):
        super().__init__(
            name="LoreKernel",
            base_url="https://lore.kernel.org/all/",
            keywords=keywords,
            year=year
        )
        # 使用Playwright模式来处理反爬虫保护
        self.http_client = HttpClient(mode="playwright")
        
    def build_search_url(self, page: int = 0) -> str:
        """
        构建 lore.kernel.org 搜索URL
        
        Args:
            page: 页码 (每页200条数据)
            
        Returns:
            搜索URL
        """
        # 构建关键词查询字符串
        keywords_query = " OR ".join([f'"{keyword}"' for keyword in self.keywords])
        
        params = {
            'q': keywords_query
        }
        
        if page > 0:
            params['o'] = page * 200
            
        base_search_url = f"{self.base_url}"
        return f"{base_search_url}?{urlencode(params)}"
        
    def crawl(self, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        爬取 lore.kernel.org 数据
        
        Args:
            max_pages: 最大页数限制
            
        Returns:
            爬取到的数据列表
        """
        all_results = []
        page = 0
        
        print(f"开始爬取 {self.name} 数据...")
        print(f"使用模式: {self.http_client.mode}")
        
        while True:
            if max_pages and page >= max_pages:
                break
                
            url = self.build_search_url(page)
            print(f"正在爬取第 {page + 1} 页: {url}")
            
            try:
                html_content = self.http_client.get(url)
                
                if not html_content:
                    print(f"第 {page + 1} 页获取失败，可能遇到反爬虫保护")
                    break
                
                # 检查是否遇到反爬虫保护页面
                if "anubis" in html_content.lower() or "proof of work" in html_content.lower():
                    print(f"检测到Anubis反爬虫保护，Playwright将自动处理...")
                    # Playwright客户端会自动处理，无需额外操作
                    
                page_results = self.parse_page(html_content)
                if not page_results:
                    print(f"第 {page + 1} 页没有数据，结束爬取")
                    break
                    
                # 过滤年份
                filtered_results = []
                for result in page_results:
                    if self.filter_by_year(result.get('date', '')):
                        filtered_results.append(result)
                        
                all_results.extend(filtered_results)
                print(f"第 {page + 1} 页获取到 {len(filtered_results)} 条有效数据")
                
                page += 1
                
                # 使用Playwright时适当增加延迟以避免被检测
                if self.http_client.mode == "playwright":
                    time.sleep(2)  # Playwright需要更多时间
                else:
                    time.sleep(1)  # requests模式保持原有延迟
                
            except Exception as e:
                print(f"爬取第 {page + 1} 页时出错: {e}")
                # 如果是Playwright相关错误，提供更详细的信息
                if "playwright" in str(e).lower():
                    print("Playwright错误，可能需要检查浏览器安装或网络连接")
                break
                
        print(f"爬取完成，共获取 {len(all_results)} 条数据")
        return all_results
        
    def parse_page(self, html_content: str) -> List[Dict[str, Any]]:
        """
        解析 lore.kernel.org 页面内容
        
        Args:
            html_content: HTML内容
            
        Returns:
            解析后的数据列表
        """
        results = []
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找邮件列表项
        # lore.kernel.org 的邮件通常在 <pre> 标签中或特定的 div 结构中
        
        # 尝试查找邮件条目
        mail_items = soup.find_all('tr') or soup.find_all('div', class_='thread')
        
        for item in mail_items:
            try:
                # 提取邮件信息
                result = self._extract_mail_info(item)
                if result and self.filter_by_keywords(result.get('content', '') + result.get('subject', '')):
                    results.append(result)
            except Exception as e:
                continue
                
        return results
        
    def _extract_mail_info(self, item) -> Optional[Dict[str, Any]]:
        """
        从邮件项目中提取信息
        
        Args:
            item: BeautifulSoup 元素
            
        Returns:
            提取的邮件信息
        """
        try:
            # 查找邮件主题
            subject_elem = item.find('a') or item.find('td', class_='subject')
            subject = subject_elem.get_text(strip=True) if subject_elem else ""
            
            # 查找邮件链接
            link_elem = item.find('a')
            link = ""
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                if href.startswith('/'):
                    link = f"{self.base_url}{href}"
                else:
                    link = href
                    
            # 查找发送者
            sender_elem = item.find('td', class_='from') or item.find_all('td')[1] if len(item.find_all('td')) > 1 else None
            sender = sender_elem.get_text(strip=True) if sender_elem else ""
            
            # 查找日期
            date_elem = item.find('td', class_='date') or item.find_all('td')[-1] if item.find_all('td') else None
            date = date_elem.get_text(strip=True) if date_elem else ""
            
            # 如果有链接，尝试获取邮件详细内容
            content = ""
            if link:
                try:
                    # 使用相同的http_client实例来保持一致的模式
                    mail_content = self.http_client.get(link)
                    if mail_content:
                        mail_soup = BeautifulSoup(mail_content, 'html.parser')
                        # 提取邮件正文
                        content_elem = mail_soup.find('pre') or mail_soup.find('div', class_='message-body')
                        if content_elem:
                            content = content_elem.get_text(strip=True)[:1000]  # 限制长度
                except Exception as e:
                    # 在Playwright模式下，某些邮件链接可能需要额外处理
                    print(f"获取邮件详细内容失败 {link}: {e}")
                    pass
                    
            if subject or content:
                return {
                    'subject': subject,
                    'sender': sender,
                    'date': date,
                    'link': link,
                    'content': content,
                    'source': self.name
                }
                
        except Exception as e:
            pass
            
        return None
