"""
配置加载器
"""

import yaml
from typing import Dict, Any, List
from pathlib import Path


class ConfigLoader:
    """配置文件加载器"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self._config = None
        
    def load_config(self) -> Dict[str, Any]:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        if self._config is None:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = yaml.safe_load(f)
            except FileNotFoundError:
                print(f"配置文件 {self.config_path} 不存在，使用默认配置")
                self._config = self._get_default_config()
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                self._config = self._get_default_config()
                
        return self._config
        
    def get_keywords(self) -> List[str]:
        """
        获取关键词列表
        
        Returns:
            关键词列表
        """
        config = self.load_config()
        return config.get('keywords', self._get_default_keywords())
        
    def get_year(self) -> int:
        """
        获取单个爬取年份（兼容旧逻辑）
        
        Returns:
            年份
        """
        years = self.get_years()
        return years[0] if years else 2025

    def get_years(self) -> List[int]:
        """
        获取爬取年份列表

        支持以下配置形式：
        - crawl_year: 2025
        - crawl_year: [2025, 2026]
        - crawl_years: [2025, 2026]

        Returns:
            年份列表
        """
        config = self.load_config()
        raw_years = config.get('crawl_years', config.get('crawl_year', 2025))
        return self._normalize_years(raw_years)
        
    def get_llm_config(self) -> Dict[str, Any]:
        """
        获取LLM配置
        
        Returns:
            LLM配置字典
        """
        config = self.load_config()
        return config.get('llm', {})
        
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            默认配置字典
        """
        return {
            'crawl_year': 2025,
            'keywords': self._get_default_keywords(),
            'llm': {
                'provider': 'deepseek',
                'api_key': '',
                'model': 'deepseek-chat',
                'base_url': 'https://api.deepseek.com',
                'timeout': 120,
                'max_retries': 2,
                'retry_backoff': 1.0,
                'use_env_proxy': False,
            },
            'output': {
                'format': 'markdown',
                'directory': 'output/reports'
            }
        }

    def _normalize_years(self, raw_years: Any) -> List[int]:
        """规范化年份配置为去重后的整数列表"""
        years: List[int] = []

        if isinstance(raw_years, int):
            years = [raw_years]
        elif isinstance(raw_years, str):
            if raw_years.strip().isdigit():
                years = [int(raw_years.strip())]
        elif isinstance(raw_years, list):
            for year in raw_years:
                try:
                    years.append(int(year))
                except (TypeError, ValueError):
                    continue

        if not years:
            return [2025]

        normalized_years: List[int] = []
        for year in years:
            if 2000 <= year <= 2100 and year not in normalized_years:
                normalized_years.append(year)

        return normalized_years or [2025]
        
    def _get_default_keywords(self) -> List[str]:
        """
        获取默认关键词列表
        
        Returns:
            默认关键词列表
        """
        return [
            "hardening", "canary", "relro", "pie", "aslr", "fortify",
            "cfi", "cet", "pac", "shadow", "safe stack", "retpoline",
            "stack clash", "security flags", "insecure binary",
            "silent security bug", "compiled without", "miscompiled",
            "endbr", "stack_chk_fail"
        ]
