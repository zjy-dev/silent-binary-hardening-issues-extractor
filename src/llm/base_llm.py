"""
基础LLM抽象类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json


class BaseLLM(ABC):
    """LLM基类，定义所有LLM客户端的通用接口"""
    
    def __init__(self, api_key: str, model: str, base_url: Optional[str] = None):
        """
        初始化LLM客户端
        
        Args:
            api_key: API密钥
            model: 模型名称
            base_url: API基础URL
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        
    @abstractmethod
    def analyze_issue(self, issue_content: str, issue_title: str = "") -> Dict[str, Any]:
        """
        分析安全问题
        
        Args:
            issue_content: 问题内容
            issue_title: 问题标题
            
        Returns:
            分析结果字典
        """
        pass
        
    def create_analysis_prompt(self, issue_content: str, issue_title: str = "") -> str:
        """
        创建分析提示词
        
        Args:
            issue_content: 问题内容
            issue_title: 问题标题
            
        Returns:
            提示词字符串
        """
        prompt = f"""
请分析以下安全相关的内容，判断是否为 Silent Bug（防御机制缺失或失效的问题）。

标题: {issue_title}

内容:
{issue_content}

请按照以下JSON格式返回分析结果：

{{
    "is_silent_bug": boolean, // 是否为silent bug
    "confidence": float, // 置信度 (0.0-1.0)
    "root_cause": "string", // 根本原因: "配置缺失" | "防御机制失效" | "编译选项错误" | "其他"
    "summary": "string", // 问题总结
    "affected_software": ["string"], // 受影响的软件列表
    "defense_mechanisms": ["string"], // 涉及的防御机制 (如: SSP, PIE, RELRO, CFI, CET, PAC等)
    "severity": "string", // 严重程度: "低" | "中" | "高"
    "recommendations": ["string"] // 修复建议
}}

Silent Bug 的特征包括：
1. 防御机制（如 Stack Canary、PIE、RELRO、ASLR、CFI 等）未启用或失效
2. 编译选项配置错误导致安全机制缺失
3. 不会引起程序崩溃但降低安全性的问题
4. 二进制文件缺少预期的安全特性

请仔细分析内容，确保判断准确。只返回JSON，不要添加其他说明。
"""
        return prompt
        
    def parse_analysis_result(self, response: str) -> Dict[str, Any]:
        """
        解析分析结果
        
        Args:
            response: LLM响应
            
        Returns:
            解析后的结果字典
        """
        try:
            # 尝试提取JSON
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # 如果找不到JSON，返回默认结果
                return self._get_default_result("无法解析LLM响应")
                
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return self._get_default_result("JSON解析失败")
        except Exception as e:
            print(f"解析分析结果时出错: {e}")
            return self._get_default_result("解析出错")
            
    def _get_default_result(self, error_msg: str) -> Dict[str, Any]:
        """
        获取默认分析结果
        
        Args:
            error_msg: 错误信息
            
        Returns:
            默认结果字典
        """
        return {
            "is_silent_bug": False,
            "confidence": 0.0,
            "root_cause": "分析失败",
            "summary": f"分析失败: {error_msg}",
            "affected_software": [],
            "defense_mechanisms": [],
            "severity": "未知",
            "recommendations": []
        }
