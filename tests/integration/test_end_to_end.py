#!/usr/bin/env python3
"""
端到端集成测试：验证爬虫获取邮件正文 + LLM 基于正文进行分析
用 mock HTML 模拟网页返回（绕过反爬），用真实 DeepSeek API 测 LLM 分析。
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.crawlers.lore_kernel_crawler import LoreKernelCrawler
from src.models.issue import Issue
from src.core.analyzer import Analyzer
from src.utils.config_loader import ConfigLoader

# ---- 模拟 HTML ----

SEARCH_PAGE_HTML = """
<html><body><pre>
1. <b><a href="msg-001/">x86/cet: fix missing SHSTK on certain Skylake CPUs</a></b>
   - by developer @ 2025-03-15 09:22 UTC [100%]

2. <b><a href="msg-002/">arm64: pac: disable pointer authentication when retpoline is on</a></b>
   - by maintainer @ 2025-04-01 14:05 UTC [100%]

3. <b><a href="msg-003/">selftests/canary: stack canary not enforced on riscv builds</a></b>
   - by tester @ 2025-02-20 07:30 UTC [100%]
</pre></body></html>
"""

EMAIL_BODIES = {
    "msg-001/": """<html><body><pre>
On certain Skylake S-series desktop CPUs, CET Shadow Stack (SHSTK) is
silently disabled after a microcode update. The CPUID enumeration still
reports CET support, but the kernel's CET activation path skips the
actual MSR_IA32_U_CET write because of a model-specific quirk table
entry that was too broad.

This means user-space binaries believe they are protected by shadow
stack, but in reality the hardware enforcement is not active.  An
attacker with arbitrary-write can overwrite return addresses without
triggering a #CP fault.

Fix: narrow the quirk to only S-stepping <= 6 and validate SHSTK
activation by reading back MSR_IA32_U_CET after the write.

Signed-off-by: developer &lt;dev@kernel.org&gt;
</pre></body></html>""",

    "msg-002/": """<html><body><pre>
When CONFIG_RETPOLINE=y is set together with CONFIG_ARM64_PTR_AUTH,
the PAC keys are still programmed at boot but the kernel never
actually enables PAC instructions for user-space because the
retpoline thunks clobber the LR signature register.

Effectively, pointer authentication is silently lost for all
user-space processes. Tools like checksec will report "PAC enabled"
based on the ELF note, but the hardware will not verify any PAC.

This silent failure reduces security posture significantly.

Signed-off-by: maintainer &lt;maint@kernel.org&gt;
</pre></body></html>""",

    "msg-003/": """<html><body><pre>
The kernel selftest for stack canary validation passes on x86 and
arm64 but silently skips the actual canary check on riscv64.

Root cause: the test uses __attribute__((stack_protect)) which is
silently ignored by the riscv gcc port (< 13.2).  The test ELF is
compiled without -fstack-protector-strong and has no __stack_chk_fail
reference, but the test harness does not verify this.

Impact: riscv64 builds ship without stack canary protection while CI
reports green. This is a textbook silent security regression.

Signed-off-by: tester &lt;test@kernel.org&gt;
</pre></body></html>""",
}


def mock_http_get(url, wait_for=None):
    """根据 URL 返回对应的 mock HTML"""
    for key, html in EMAIL_BODIES.items():
        if key in url:
            return html
    # 默认返回搜索页
    return SEARCH_PAGE_HTML


def main():
    config_loader = ConfigLoader()
    llm_config = config_loader.get_llm_config()

    # ---- 1. 爬取（mock HTTP）----
    print("=" * 60)
    print("[1/3] 爬虫解析 + 邮件正文获取（mock HTTP）")
    print("=" * 60)

    keywords = ["hardening", "canary", "cet", "pac", "retpoline"]
    crawler = LoreKernelCrawler(keywords, year=2025)

    with patch.object(crawler.http_client, "get", side_effect=mock_http_get):
        raw_data = crawler.crawl(max_pages=1)

    if not raw_data:
        print("❌ 爬虫解析失败，无数据")
        sys.exit(1)

    # ---- 2. 验证正文是否被获取 ----
    print(f"\n共解析 {len(raw_data)} 条结果")
    print("=" * 60)
    print("[2/3] 验证邮件正文获取")
    print("=" * 60)

    issues = []
    content_fetched_count = 0
    for item in raw_data:
        subject = item.get("subject", "")
        content = item.get("content", "")
        is_enriched = content != subject and len(content) > len(subject)
        if is_enriched:
            content_fetched_count += 1
        status = "✅ 有正文" if is_enriched else "⚠️  仅标题"
        print(f"\n{status}")
        print(f"  标题: {subject[:80]}")
        print(f"  正文长度: {len(content)} 字符")
        if is_enriched:
            print(f"  正文预览: {content[:120]}...")

        issues.append(Issue(
            title=subject,
            content=content,
            source=item.get("source", ""),
            url=item.get("link", ""),
            date=item.get("date", ""),
            author=item.get("sender", ""),
            raw_data=item,
        ))

    print(f"\n📊 正文获取率: {content_fetched_count}/{len(issues)}")
    if content_fetched_count == 0:
        print("❌ 没有成功获取任何邮件正文，bug 未修复！")
        sys.exit(1)
    else:
        print("✅ 邮件正文已正确获取，bug 已修复")

    # ---- 3. 真实 LLM 分析 ----
    print("\n" + "=" * 60)
    print("[3/3] DeepSeek LLM 分析（真实 API 调用）")
    print("=" * 60)

    if not llm_config.get("api_key"):
        print("⚠️  未配置 API Key，跳过 LLM 分析")
        sys.exit(0)

    analyzer = Analyzer.create_analyzer_from_config(llm_config)
    analyzed = analyzer.analyze_issues(issues)

    for issue, result in analyzed:
        print(f"\n--- {issue.title[:60]} ---")
        print(f"  is_silent_bug: {result.is_silent_bug}")
        print(f"  confidence:    {result.confidence}")
        print(f"  severity:      {result.severity}")
        print(f"  summary:       {result.summary[:200]}")
        print(f"  root_cause:    {result.root_cause}")
        # 验证 summary 中包含正文相关的细节，而不只是复述标题
        title_words = set(issue.title.lower().split())
        summary_words = set(result.summary.lower().split())
        extra_words = summary_words - title_words
        if len(extra_words) > 5:
            print("  ✅ LLM 总结包含正文中的额外信息")
        else:
            print("  ⚠️  LLM 总结可能只基于标题")

    print("\n" + "=" * 60)
    print("✅ 集成测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
