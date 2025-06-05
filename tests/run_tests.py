#!/usr/bin/env python3
"""
测试运行器 - 运行所有测试
"""

import unittest
import sys
from pathlib import Path

# 添加项目路径
ROOT_DIR = Path(__file__).parent.parent
SRC_DIR = ROOT_DIR / "src"
sys.path.insert(0, str(SRC_DIR))

def run_unit_tests():
    """运行单元测试"""
    print("🧪 运行单元测试...")
    print("=" * 50)
    
    # 发现并运行单元测试
    loader = unittest.TestLoader()
    start_dir = ROOT_DIR / "tests" / "unit"
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_integration_tests():
    """运行集成测试"""
    print("\n🔗 运行集成测试...")
    print("=" * 50)
    
    # 发现并运行集成测试
    loader = unittest.TestLoader()
    start_dir = ROOT_DIR / "tests" / "integration"
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行所有测试...")
    print("=" * 60)
    
    unit_success = run_unit_tests()
    integration_success = run_integration_tests()
    
    print("\n" + "=" * 60)
    print("📊 测试总结:")
    print(f"   单元测试: {'✅ 通过' if unit_success else '❌ 失败'}")
    print(f"   集成测试: {'✅ 通过' if integration_success else '❌ 失败'}")
    
    if unit_success and integration_success:
        print("\n🎉 所有测试通过！")
        return True
    else:
        print("\n⚠️  部分测试失败，请检查代码")
        return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='运行项目测试')
    parser.add_argument('--unit', action='store_true', help='只运行单元测试')
    parser.add_argument('--integration', action='store_true', help='只运行集成测试')
    parser.add_argument('--all', action='store_true', help='运行所有测试（默认）')
    
    args = parser.parse_args()
    
    if args.unit:
        success = run_unit_tests()
    elif args.integration:
        success = run_integration_tests()
    else:
        success = run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
