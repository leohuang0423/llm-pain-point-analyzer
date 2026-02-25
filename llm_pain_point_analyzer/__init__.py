"""
LLM-PainPoint-Analyzer - 解决大模型作为第一用户的三大核心痛点

三大核心痛点：
1. 权限认知偏差 - 解决权限问题
2. 工具选择决策困难 - 智能工具推荐
3. 操作模式混淆 - 智能错误诊断

核心模块：
- permission_analyzer: 权限分析器
- tool_recommender: 工具推荐器
- error_diagnoser: 错误诊断器
- permission_verifier: 权限验证器
"""

__version__ = "1.0.0"
__author__ = "LeoClaw"
__description__ = "LLM痛点分析器 - 解决大模型作为第一用户的三大核心痛点"

from .permission_analyzer import PermissionAnalyzer
from .tool_recommender import ToolRecommender
from .error_diagnoser import ErrorDiagnoser
from .permission_verifier import PermissionVerifier

__all__ = [
    "PermissionAnalyzer",
    "ToolRecommender", 
    "ErrorDiagnoser",
    "PermissionVerifier",
    "__version__",
    "__author__",
    "__description__"
]