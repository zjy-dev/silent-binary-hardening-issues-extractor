"""
测试配置和公共工具
"""
import sys
from pathlib import Path

# 添加src目录到Python路径
ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))


class TestConfig:
    """测试配置类"""
    
    # 测试数据
    SAMPLE_KEYWORDS = ["hardening", "canary", "stack-protection"]
    TEST_YEAR = 2025
    
    # 测试URL和数据
    SAMPLE_ISSUE_DATA = {
        "title": "Test Stack Canary Issue",
        "content": "This is a test content about stack canary protection",
        "source": "lore.kernel.org",
        "url": "https://lore.kernel.org/test/123456",
        "date": "2025-01-01",
        "author": "test@example.com"
    }
    
    SAMPLE_ANALYSIS_DATA = {
        "is_silent_bug": True,
        "confidence": 0.9,
        "root_cause": "配置缺失",
        "summary": "Stack canary 未启用"
    }


def get_src_path():
    """获取src目录路径"""
    return SRC_DIR


def get_test_data_path():
    """获取测试数据目录路径"""
    return ROOT_DIR / "tests" / "fixtures"
