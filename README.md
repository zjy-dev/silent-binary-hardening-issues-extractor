# Silent Binary Hardening Issues Extractor

🔍 **自动化检测二进制防御机制缺失的 Silent Bug 提取工具**

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📌 项目简介

Silent Binary Hardening Issues Extractor 是一个专门用于自动化发现和分析 **Silent Bug** 的工具。这些 Silent Bug 是指不会引起程序运行异常，但会降低安全保障的防御机制缺失或失效问题。

本项目通过多态架构设计，支持从多个安全相关数据源（邮件列表、Bug 追踪系统等）爬取数据，并使用大语言模型进行智能分析，识别潜在的二进制防御机制问题。

## 🎯 核心功能

- 🕷️ **多源数据爬取**: 支持从 lore.kernel.org 等安全邮件列表爬取相关信息
- 🧠 **智能分析**: 使用 DeepSeek 等大语言模型进行语义分析
- 📊 **结构化报告**: 生成 Markdown 和 JSON 格式的详细报告
- 🔧 **可扩展架构**: 基于多态设计，易于扩展新的数据源和分析器
- ⚙️ **灵活配置**: 支持 YAML 配置文件和环境变量

## 🛡️ 检测的防御机制

项目专注于检测以下二进制防御机制的缺失或失效：

- **Stack Canary (SSP)** - 栈溢出保护
- **PIE** - 位置无关可执行文件
- **RELRO** - 只读重定位
- **ASLR** - 地址空间布局随机化
- **CFI** - 控制流完整性
- **CET** - 控制流增强技术
- **PAC** - 指针认证
- **SafeStack** - 安全栈
- **ShadowCallStack** - 影子调用栈
- **Fortify** - 源码强化

## 🚀 快速开始

### 环境要求

- Python 3.13+
- uv (推荐的 Python 包管理器)

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd silent-binary-hardening-issues-extractor

# 使用 uv 创建虚拟环境并安装依赖
uv sync
```

### 配置

1. 复制配置文件模板：

```bash
cp .env.example .env
```

2. 编辑配置文件 `config/config.yaml`，设置你的 DeepSeek API Key：

```yaml
llm:
  provider: "deepseek"
  api_key: "your_deepseek_api_key_here"
  model: "deepseek-chat"
  base_url: "https://api.deepseek.com"
```

或者设置环境变量：

```bash
export DEEPSEEK_API_KEY="your_deepseek_api_key_here"
```

### 运行

```bash
# 运行主程序
uv run python src/main.py

# 或者使用安装的命令
uv run silent-extractor
```

### 测试

```bash
# 运行测试脚本
uv run python test.py
```

## 📁 项目结构

```
silent-binary-hardening-issues-extractor/
├── src/
│   ├── core/                  # 核心模块
│   │   ├── base_crawler.py    # 爬虫基类
│   │   ├── analyzer.py        # 数据分析器
│   │   └── reporter.py        # 报告生成器
│   ├── crawlers/              # 爬虫实现
│   │   ├── crawler_factory.py # 爬虫工厂
│   │   └── lore_kernel_crawler.py # Lore Kernel爬虫
│   ├── llm/                   # 大语言模型客户端
│   │   ├── base_llm.py        # LLM基类
│   │   └── deepseek_client.py # DeepSeek客户端
│   ├── models/                # 数据模型
│   │   └── issue.py           # Issue和AnalysisResult模型
│   ├── utils/                 # 工具模块
│   │   ├── config_loader.py   # 配置加载器
│   │   └── http_client.py     # HTTP客户端
│   └── main.py                # 主程序入口
├── config/
│   └── config.yaml            # 配置文件
├── output/                    # 输出目录
│   └── reports/               # 报告文件
├── test.py                    # 测试脚本
└── README.md                  # 项目文档
```

## 🔧 配置说明

### config.yaml 配置项

```yaml
# 爬取设置
crawl_year: 2025 # 爬取年份

# 关键词列表 - 用于过滤相关内容
keywords:
  - "hardening"
  - "canary"
  - "relro"
  # ... 更多关键词

# LLM设置
llm:
  provider: "deepseek" # LLM提供商
  api_key: "" # API密钥
  model: "deepseek-chat" # 模型名称
  base_url: "https://api.deepseek.com"

# 输出设置
output:
  format: "markdown" # 输出格式
  directory: "output/reports" # 输出目录

# 分析设置
analysis:
  min_confidence: 0.6 # 最小置信度阈值
  batch_size: 10 # 批量分析大小
```

## 📊 使用示例

运行程序后，将在 `output/reports/` 目录生成报告：

- `silent_bugs_report_YYYYMMDD_HHMMSS.md` - 详细的 Markdown 报告
- `silent_bugs_summary_YYYYMMDD_HHMMSS.json` - JSON 格式摘要

## 🏗️ 架构设计

项目采用多态架构设计，主要组件：

### 1. 爬虫层 (Crawlers)

- `BaseCrawler`: 抽象基类，定义爬虫接口
- `LoreKernelCrawler`: Lore Kernel 邮件列表爬虫实现
- `CrawlerFactory`: 爬虫工厂，支持动态创建爬虫

### 2. 分析层 (Analysis)

- `BaseLLM`: LLM 抽象基类
- `DeepSeekClient`: DeepSeek API 客户端实现
- `Analyzer`: 数据分析器，协调 LLM 分析

### 3. 数据层 (Models)

- `Issue`: 问题数据模型
- `AnalysisResult`: 分析结果模型

### 4. 工具层 (Utils)

- `ConfigLoader`: 配置加载器
- `HttpClient`: HTTP 请求客户端
- `Reporter`: 报告生成器

## 🔍 支持的数据源

### 当前支持

- **Lore Kernel** (https://lore.kernel.org/) - Linux 内核邮件列表

### 计划支持

- OSS Security 邮件列表
- GCC/LLVM Bugzilla
- Debian/Red Hat Bug Tracker
- 各大厂商安全博客

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

### 添加新爬虫

1. 继承 `BaseCrawler` 类
2. 实现必要的抽象方法
3. 在 `CrawlerFactory` 中注册新爬虫
4. 添加相应的测试

### 添加新 LLM 客户端

1. 继承 `BaseLLM` 类
2. 实现 `analyze_issue` 方法
3. 在 `Analyzer` 中添加支持
4. 更新配置文件

## 📝 开发计划

### TODO List

#### 🔥 核心功能

- [x] 基础架构设计 (多态模式)
- [x] Lore Kernel 爬虫实现
- [x] DeepSeek LLM 集成
- [x] 配置系统
- [x] 基础测试
- [ ] 完整的单元测试覆盖
- [ ] 集成测试
- [ ] 性能优化

#### 🕷️ 爬虫扩展

- [ ] OSS Security 邮件列表爬虫
- [ ] GCC Bugzilla 爬虫
- [ ] LLVM GitHub Issues 爬虫
- [ ] Debian Bug Tracker 爬虫
- [ ] Red Hat Bugzilla 爬虫
- [ ] CVE 数据库集成

#### 🧠 分析增强

- [ ] OpenAI GPT 客户端
- [ ] Claude 客户端
- [ ] 本地 LLM 支持 (Ollama)
- [ ] 多模型结果融合
- [ ] 误报率优化
- [ ] 自定义分析规则

#### 📊 报告系统

- [ ] HTML 报告生成
- [ ] PDF 报告导出
- [ ] 邮件通知功能
- [ ] 实时仪表板
- [ ] 趋势分析
- [ ] 统计图表

#### 🔧 工具完善

- [ ] CLI 参数支持
- [ ] Docker 容器化
- [ ] CI/CD 流水线
- [ ] 分布式爬取
- [ ] 数据库持久化
- [ ] Web 界面

#### 📈 监控运维

- [ ] 日志系统完善
- [ ] 错误处理优化
- [ ] 性能监控
- [ ] 自动重试机制
- [ ] 代理支持
- [ ] 速率限制

## 📄 许可证

本项目使用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [DeepSeek](https://www.deepseek.com/) - 提供强大的 LLM 分析能力
- [Lore Kernel](https://lore.kernel.org/) - Linux 内核邮件列表
- 所有为开源安全做出贡献的研究者和开发者

## 📞 联系方式

- 项目地址: [GitHub Repository]
- 问题反馈: [GitHub Issues]

---

**⚠️ 免责声明**: 本工具仅用于安全研究和教育目的。使用时请遵守相关网站的服务条款和法律法规。
