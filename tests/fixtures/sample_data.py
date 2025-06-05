# 测试数据样本

# 模拟的 Lore Kernel 响应数据
SAMPLE_LORE_RESPONSE = {
    "messages": [
        {
            "subject": "[PATCH] x86/stackprotector: Enable stack canary for GCC builds",
            "sender": "security@kernel.org",
            "date": "2025-01-15T14:30:00Z",
            "body": "This patch enables stack canary protection for all GCC builds to prevent stack-based buffer overflow attacks. The implementation adds -fstack-protector-strong flag to the build configuration."
        },
        {
            "subject": "[RFC] arm64: Add hardware hardening support",
            "sender": "arm-dev@lists.kernel.org", 
            "date": "2025-01-20T09:15:00Z",
            "body": "This RFC proposes adding hardware-assisted security hardening features for ARM64 architecture including pointer authentication and branch target identification."
        },
        {
            "subject": "[BUG] Silent failure in FORTIFY_SOURCE detection",
            "sender": "bugs@kernel.org",
            "date": "2025-01-25T16:45:00Z",
            "body": "Report about silent failures in FORTIFY_SOURCE detection mechanism. The issue occurs when buffer overflow checks are bypassed due to compiler optimization."
        }
    ]
}

# 测试关键词
TEST_KEYWORDS = [
    "hardening",
    "canary", 
    "stack-protector",
    "fortify",
    "aslr",
    "smep",
    "smap",
    "cfi"
]

# 测试配置
TEST_CONFIG = {
    "keywords": TEST_KEYWORDS,
    "year": 2025,
    "max_pages": 1
}
