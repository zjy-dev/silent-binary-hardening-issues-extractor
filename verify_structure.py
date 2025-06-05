#!/usr/bin/env python3
"""
快速验证脚本 - 验证重构后的测试结构是否正常工作
"""

import sys
from pathlib import Path

# 添加项目路径
ROOT_DIR = Path(__file__).parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

def test_imports():
    """测试关键模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        from utils.config_loader import ConfigLoader
        print("✅ ConfigLoader 导入成功")
        
        from crawlers.lore_kernel_crawler import LoreKernelCrawler
        print("✅ LoreKernelCrawler 导入成功")
        
        from models.issue import Issue, AnalysisResult
        print("✅ Issue 和 AnalysisResult 模型导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n🧪 测试基本功能...")
    
    try:
        from utils.config_loader import ConfigLoader
        from crawlers.lore_kernel_crawler import LoreKernelCrawler
        from models.issue import Issue
        
        # 测试配置加载
        config = ConfigLoader()
        keywords = config.get_keywords()
        year = config.get_year()
        print(f"✅ 配置加载成功 - 关键词: {len(keywords)}个, 年份: {year}")
        
        # 测试爬虫创建
        crawler = LoreKernelCrawler(keywords[:3], year)  # 使用前3个关键词
        url = crawler.build_search_url(0)
        print(f"✅ 爬虫创建成功 - URL: {url[:50]}...")
        
        # 测试Issue模型
        issue = Issue(
            title="Test Issue",
            content="Test content",
            source="test",
            url="http://test.com",
            date="2025-01-01",
            author="test@test.com"
        )
        issue_dict = issue.to_dict()
        print("✅ Issue模型创建成功")
        
        return True
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False

def test_directory_structure():
    """测试目录结构"""
    print("\n📁 验证目录结构...")
    
    expected_paths = [
        ROOT_DIR / "tests",
        ROOT_DIR / "tests" / "unit",
        ROOT_DIR / "tests" / "integration", 
        ROOT_DIR / "tests" / "fixtures",
        ROOT_DIR / "tests" / "unit" / "test_config_loader.py",
        ROOT_DIR / "tests" / "unit" / "test_models.py",
        ROOT_DIR / "tests" / "unit" / "test_lore_kernel_crawler.py",
        ROOT_DIR / "tests" / "integration" / "test_crawler_workflow.py",
        ROOT_DIR / "tests" / "run_tests.py"
    ]
    
    all_exist = True
    for path in expected_paths:
        if path.exists():
            print(f"✅ {path.relative_to(ROOT_DIR)}")
        else:
            print(f"❌ {path.relative_to(ROOT_DIR)} 不存在")
            all_exist = False
    
    # 检查不应该存在的文件
    old_files = [
        ROOT_DIR / "demo.py",
        ROOT_DIR / "test.py"
    ]
    
    for old_file in old_files:
        if not old_file.exists():
            print(f"✅ {old_file.name} 已删除")
        else:
            print(f"❌ {old_file.name} 仍然存在")
            all_exist = False
    
    return all_exist

def main():
    """主验证函数"""
    print("🚀 开始验证重构后的项目结构...")
    print("=" * 60)
    
    # 运行所有验证测试
    tests = [
        ("目录结构", test_directory_structure),
        ("模块导入", test_imports),
        ("基本功能", test_basic_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 验证通过")
        else:
            print(f"❌ {test_name} 验证失败")
    
    print("\n" + "=" * 60)
    print(f"📊 验证结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 项目重构验证成功！")
        print("\n📝 后续操作建议：")
        print("1. 运行测试: python tests/run_tests.py")
        print("2. 运行单元测试: python tests/run_tests.py --unit")
        print("3. 运行集成测试: python tests/run_tests.py --integration")
        print("4. 运行主程序: python main.py")
    else:
        print("⚠️  项目重构存在问题，请检查上述错误")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
