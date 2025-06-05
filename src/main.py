"""
主程序入口
"""

import sys
import os
from pathlib import Path
from typing import List

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.config_loader import ConfigLoader
from src.crawlers.crawler_factory import CrawlerFactory
from src.models.issue import Issue
from src.core.analyzer import Analyzer
from src.core.reporter import Reporter


def main():
    """主程序入口"""
    print("🚀 Silent Binary Hardening Issues Extractor 启动")
    print("=" * 60)
    
    # 加载配置
    print("📋 加载配置...")
    config_loader = ConfigLoader()
    keywords = config_loader.get_keywords()
    year = config_loader.get_year()
    llm_config = config_loader.get_llm_config()
    
    print(f"关键词: {', '.join(keywords[:5])}... (共{len(keywords)}个)")
    print(f"爬取年份: {year}")
    print()
    
    # 检查API Key
    if not llm_config.get('api_key'):
        print("⚠️  警告: 未配置LLM API Key，请在config/config.yaml中配置或设置环境变量DEEPSEEK_API_KEY")
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if api_key:
            llm_config['api_key'] = api_key
            print("✅ 从环境变量获取到API Key")
        else:
            print("❌ 未找到API Key，将无法进行LLM分析")
            return
    
    # 创建爬虫
    print("🕷️  创建爬虫...")
    crawlers = CrawlerFactory.create_all_crawlers(keywords, year)
    print(f"创建了 {len(crawlers)} 个爬虫")
    
    # 爬取数据
    all_issues = []
    for crawler in crawlers:
        print(f"\n📥 使用 {crawler.name} 爬虫爬取数据...")
        try:
            raw_data = crawler.crawl(max_pages=3)  # 限制前3页，避免爬取太久
            
            # 转换为Issue对象
            for item in raw_data:
                issue = Issue(
                    title=item.get('subject', ''),
                    content=item.get('content', ''),
                    source=item.get('source', crawler.name),
                    url=item.get('link', ''),
                    date=item.get('date', ''),
                    author=item.get('sender', ''),
                    raw_data=item
                )
                all_issues.append(issue)
                
        except Exception as e:
            print(f"❌ 爬虫 {crawler.name} 执行失败: {e}")
            
    print(f"\n📊 总共爬取到 {len(all_issues)} 个问题")
    
    if not all_issues:
        print("❌ 未爬取到任何数据，程序退出")
        return
        
    # LLM分析
    print(f"\n🧠 开始LLM分析...")
    try:
        analyzer = Analyzer.create_analyzer_from_config(llm_config)
        analyzed_results = analyzer.analyze_issues(all_issues)
        
        # 过滤Silent Bug
        silent_bugs = analyzer.filter_silent_bugs(analyzed_results, min_confidence=0.6)
        
    except Exception as e:
        print(f"❌ LLM分析失败: {e}")
        return
        
    # 生成报告
    print(f"\n📝 生成报告...")
    try:
        reporter = Reporter()
        
        # 生成Markdown报告
        markdown_path = reporter.generate_report(silent_bugs)
        
        # 生成JSON摘要
        json_path = reporter.generate_summary_json(silent_bugs)
        
        print(f"✅ 报告生成完成:")
        print(f"   - Markdown报告: {markdown_path}")
        print(f"   - JSON摘要: {json_path}")
        
    except Exception as e:
        print(f"❌ 报告生成失败: {e}")
        
    print(f"\n🎉 程序执行完成!")
    print(f"发现 {len(silent_bugs)} 个Silent Bug")


if __name__ == "__main__":
    main()
