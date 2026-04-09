"""
主程序入口
"""

import sys
import os
from pathlib import Path

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
    years = config_loader.get_years()
    llm_config = config_loader.get_llm_config()
    max_pages = config_loader.load_config().get('crawlers', {}).get('max_pages', 3)
    
    print(f"关键词: {', '.join(keywords[:5])}... (共{len(keywords)}个)")
    print(f"爬取年份: {', '.join(str(year) for year in years)}")
    print()
    
    # 检查API Key
    if not llm_config.get('api_key'):
        print("⚠️  警告: 未配置LLM API Key，请在config/config.yaml中配置或设置环境变量 LLM_API_KEY/OPENAI_API_KEY/DEEPSEEK_API_KEY")
        env_key_names = ['LLM_API_KEY', 'OPENAI_API_KEY', 'DEEPSEEK_API_KEY']

        for env_key_name in env_key_names:
            api_key = os.getenv(env_key_name)
            if api_key:
                llm_config['api_key'] = api_key
                print(f"✅ 从环境变量 {env_key_name} 获取到API Key")
                break

        if not llm_config.get('api_key'):
            print("❌ 未找到API Key，将无法进行LLM分析")
            return
    
    # 创建爬虫
    print("🕷️  创建爬虫...")
    crawlers = CrawlerFactory.create_all_crawlers(keywords, years)
    print(f"创建了 {len(crawlers)} 个爬虫")
    
    # 爬取数据
    all_issues = []
    for crawler in crawlers:
        print(f"\n📥 使用 {crawler.name} 爬虫爬取数据...")
        try:
            raw_data = crawler.crawl(max_pages=max_pages)
            
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

    # 去重，避免重复问题触发重复LLM请求
    unique_issues = []
    seen_issue_keys = set()
    for issue in all_issues:
        issue_key = (issue.url.strip(), issue.title.strip())
        if issue_key in seen_issue_keys:
            continue
        seen_issue_keys.add(issue_key)
        unique_issues.append(issue)

    if len(unique_issues) < len(all_issues):
        print(f"🔁 去重: {len(all_issues)} -> {len(unique_issues)}")
    all_issues = unique_issues
            
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
