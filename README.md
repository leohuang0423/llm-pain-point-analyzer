# LLM-PainPoint-Analyzer

LLM痛点分析器 - 解决大模型作为第一用户的三大核心痛点

## 🎯 核心痛点

基于OpenClaw实际使用经验，识别大模型作为第一用户的三大核心痛点：

### 1. 权限认知偏差
- **问题**: API设计未考虑大模型调用模式，权限系统不符合直觉
- **症状**: "我知道我需要做什么，但不知道我是否有权限"
- **解决方案**: 智能权限验证和预检系统

### 2. 工具选择决策困难
- **问题**: 工具生态系统缺乏智能协调，选择困难
- **症状**: "有太多工具，我不知道该用哪个"
- **解决方案**: 基于任务复杂度的智能工具推荐

### 3. 操作模式混淆
- **问题**: API参数依赖关系不直观，错误信息不明确
- **症状**: "我知道怎么操作，但总是出错"
- **解决方案**: 智能错误诊断和操作指导

## 📦 安装

```bash
# 从PyPI安装
pip install llm-pain-point-analyzer

# 从源码安装
git clone https://github.com/yourusername/llm-pain-point-analyzer.git
cd llm-pain-point-analyzer
pip install -e .
```

## 🚀 快速开始

### 1. 权限分析
```python
from llm_pain_point_analyzer import PermissionAnalyzer

analyzer = PermissionAnalyzer()
analysis = analyzer.analyze_permission_issue(
    error_message="权限不足，操作被拒绝",
    tool_name="feishu_doc",
    action="create"
)
print(analysis)
```

### 2. 工具推荐
```python
from llm_pain_point_analyzer import ToolRecommender

recommender = ToolRecommender()
recommendation = recommender.recommend_tool(
    task_description="搜索OpenClaw的最新文档",
    task_complexity="medium",
    available_tools=["web_search", "web_fetch", "read"]
)
print(recommendation)
```

### 3. 错误诊断
```python
from llm_pain_point_analyzer import ErrorDiagnoser

diagnoser = ErrorDiagnoser()
diagnosis = diagnoser.diagnose_error(
    error_message="文档创建成功但标题显示完整内容",
    tool_name="feishu_doc",
    action="create"
)
print(diagnosis)
```

### 4. 权限验证
```python
from llm_pain_point_analyzer import PermissionVerifier

verifier = PermissionVerifier()
verification = verifier.verify_permission(
    available_scopes=["docx:document:read_only"],
    required_scopes=["docx:document:write_only"]
)
print(verification)
```

## 📋 命令行工具

### 权限分析
```bash
llm-pain-analyze "权限不足，操作被拒绝" --tool feishu_doc --action create
```

### 工具推荐
```bash
llm-tool-recommend "搜索OpenClaw的最新文档" --complexity medium
```

### 错误诊断
```bash
llm-error-diagnose "文档创建成功但标题显示完整内容" --tool feishu_doc --action create
```

### 权限验证
```bash
llm-permission-verify --tool feishu_doc --action create --available-scopes '["docx:document:read_only"]'
```

## 🏗️ 架构设计

### 核心模块
```
llm_pain_point_analyzer/
├── __init__.py              # 包入口
├── permission_analyzer.py   # 权限分析器
├── tool_recommender.py      # 工具推荐器
├── error_diagnoser.py       # 错误诊断器
└── permission_verifier.py   # 权限验证器
```

### 配置文件
```
config/
├── permission_mappings.json    # 权限映射
├── tool_requirements.json      # 工具需求
├── error_patterns.json         # 错误模式
├── solution_templates.json     # 解决方案模板
├── common_mistakes.json        # 常见错误
├── scope_descriptions.json     # 权限范围描述
└── permission_hierarchy.json   # 权限层级
```

## 🔧 配置

### 自定义配置
```python
from llm_pain_point_analyzer import PermissionAnalyzer

# 使用自定义配置目录
analyzer = PermissionAnalyzer(config_dir="/path/to/your/config")
```

### 配置文件示例
```json
{
  "permission_mappings": {
    "feishu_doc": {
      "create": ["docx:document:create", "docx:document:write_only"],
      "read": ["docx:document:read_only"]
    }
  }
}
```

## 📊 使用案例

### 案例1: 飞书文档创建问题
**问题**: 创建文档时内容被写入标题
**解决方案**: 使用两步操作法
```python
# 错误方式
feishu_doc.create(title="报告", content="完整报告内容...")

# 正确方式
# 1. 创建只有标题的文档
doc = feishu_doc.create(title="报告", content="报告")
# 2. 使用update_block添加正文
feishu_doc.update_block(doc_token=doc.id, block_id=doc.id, content="完整报告内容...")
```

### 案例2: 搜索工具选择
**问题**: 不知道使用哪个搜索工具
**解决方案**: 智能工具推荐
```python
recommendation = recommender.recommend_tool(
    task_description="搜索中文技术文档",
    task_complexity="low",
    available_tools=["web_search", "baidu_search", "ddg_search"]
)
# 推荐: baidu_search (中文搜索效果更好)
```

### 案例3: 权限验证
**问题**: 不确定是否有足够权限
**解决方案**: 权限预检
```python
verification = verifier.verify_permission(
    available_scopes=current_scopes,
    required_scopes=verifier.get_required_scopes("feishu_doc", "create")
)
if not verification["verification_passed"]:
    print(f"缺失权限: {verification['missing_scopes']}")
```

## 🎨 设计理念

### 基于实际使用经验
- 所有痛点识别都基于OpenClaw实际使用经验
- 解决方案经过实际验证
- 持续更新和改进

### 大模型友好
- API设计考虑大模型调用模式
- 错误信息明确且可操作
- 配置简单直观

### 可扩展性
- 模块化设计，易于扩展
- 支持自定义配置
- 插件化架构

## 🤝 贡献

欢迎贡献！请查看[贡献指南](CONTRIBUTING.md)。

### 开发环境设置
```bash
# 克隆仓库
git clone https://github.com/yourusername/llm-pain-point-analyzer.git
cd llm-pain-point-analyzer

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black llm_pain_point_analyzer tests
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢OpenClaw社区的实际使用反馈
- 感谢所有贡献者的宝贵建议
- 特别感谢用户对三大痛点的深度分析和验证

## 📞 支持

- 问题报告: [GitHub Issues](https://github.com/yourusername/llm-pain-point-analyzer/issues)
- 文档: [项目Wiki](https://github.com/yourusername/llm-pain-point-analyzer/wiki)
- 讨论: [GitHub Discussions](https://github.com/yourusername/llm-pain-point-analyzer/discussions)

---

**LLM痛点分析器** - 让大模型使用工具更简单、更智能、更高效！