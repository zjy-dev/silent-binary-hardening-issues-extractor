"""
数据模型定义
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class Issue:
    """安全问题数据模型"""
    
    title: str
    content: str
    source: str
    url: str
    date: str
    author: Optional[str] = None
    tags: Optional[List[str]] = None
    raw_data: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.tags is None:
            self.tags = []
            
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'title': self.title,
            'content': self.content,
            'source': self.source,
            'url': self.url,
            'date': self.date,
            'author': self.author,
            'tags': self.tags,
            'raw_data': self.raw_data
        }


@dataclass
class AnalysisResult:
    """分析结果数据模型"""
    
    is_silent_bug: bool
    confidence: float
    root_cause: str
    summary: str
    affected_software: Optional[List[str]] = None
    defense_mechanisms: Optional[List[str]] = None
    severity: Optional[str] = None
    recommendations: Optional[List[str]] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if self.affected_software is None:
            self.affected_software = []
        if self.defense_mechanisms is None:
            self.defense_mechanisms = []
        if self.recommendations is None:
            self.recommendations = []
            
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'is_silent_bug': self.is_silent_bug,
            'confidence': self.confidence,
            'root_cause': self.root_cause,
            'summary': self.summary,
            'affected_software': self.affected_software,
            'defense_mechanisms': self.defense_mechanisms,
            'severity': self.severity,
            'recommendations': self.recommendations
        }
