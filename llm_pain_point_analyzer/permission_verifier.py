#!/usr/bin/env python3
"""
LLM痛点分析器 - 权限验证模块
解决权限认知偏差问题
"""

import json
import sys
import re
import argparse
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
import subprocess
from collections import defaultdict

class PermissionVerifier:
    """智能权限验证器"""
    
    def __init__(self, config_dir: str = None):
        """初始化权限验证器"""
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(__file__), "../config")
        
        self.config_dir = Path(config_dir)
        self.permission_mappings = self.load_permission_mappings()
        self.tool_requirements = self.load_tool_requirements()
        self.scope_descriptions = self.load_scope_descriptions()
        self.permission_hierarchy = self.load_permission_hierarchy()
        
    def load_permission_mappings(self) -> Dict:
        """加载权限映射"""
        mappings_file = self.config_dir / "permission_mappings.json"
        if mappings_file.exists():
            with open(mappings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认权限映射
        return {
            "document_operations": {
                "feishu_doc": {
                    "create": ["docx:document:create", "docx:document:write_only"],
                    "read": ["docx:document:read_only"],
                    "write": ["docx:document:write_only"],
                    "update_block": ["docx:document:write_only"],
                    "list_blocks": ["docx:document:read_only"]
                },
                "feishu_wiki": {
                    "create": ["wiki:wiki:write_only"],
                    "read": ["wiki:wiki:read_only"],
                    "search": ["wiki:wiki:read_only"]
                }
            },
            "file_operations": {
                "feishu_drive": {
                    "list": ["drive:drive:read_only"],
                    "create_folder": ["drive:drive:write_only"],
                    "move": ["drive:drive:write_only"],
                    "delete": ["drive:drive:write_only"]
                },
                "read": {
                    "read": ["file:read"]  # 本地文件读取
                },
                "write": {
                    "write": ["file:write"]  # 本地文件写入
                },
                "edit": {
                    "edit": ["file:write"]  # 本地文件编辑
                }
            },
            "search_operations": {
                "web_search": {
                    "search": ["search:web"]  # 网页搜索
                },
                "web_fetch": {
                    "fetch": ["web:fetch"]  # 网页提取
                }
            },
            "system_operations": {
                "exec": {
                    "exec": ["system:exec"]  # 系统执行
                },
                "process": {
                    "process": ["system:process"]  # 进程管理
                }
            },
            "messaging_operations": {
                "message": {
                    "send": ["message:send"]  # 消息发送
                }
            }
        }
    
    def load_tool_requirements(self) -> Dict:
        """加载工具需求"""
        requirements_file = self.config_dir / "tool_requirements.json"
        if requirements_file.exists():
            with open(requirements_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认工具需求
        return {
            "feishu_doc": {
                "description": "飞书文档操作",
                "required_scopes": ["docx:document:read_only", "docx:document:write_only"],
                "optional_scopes": ["docx:document:create"],
                "common_permission_issues": [
                    {
                        "issue": "创建文档时内容写入标题",
                        "required_scope": "docx:document:write_only",
                        "workaround": "使用update_block添加内容"
                    }
                ]
            },
            "feishu_drive": {
                "description": "飞书云存储操作",
                "required_scopes": ["drive:drive:read_only"],
                "optional_scopes": ["drive:drive:write_only"],
                "common_permission_issues": [
                    {
                        "issue": "无法创建文件夹",
                        "required_scope": "drive:drive:write_only",
                        "workaround": "申请写入权限"
                    }
                ]
            },
            "feishu_wiki": {
                "description": "飞书知识库操作",
                "required_scopes": ["wiki:wiki:read_only"],
                "optional_scopes": ["wiki:wiki:write_only"],
                "common_permission_issues": []
            },
            "web_search": {
                "description": "网页搜索",
                "required_scopes": ["search:web"],
                "optional_scopes": [],
                "common_permission_issues": [
                    {
                        "issue": "API密钥未配置",
                        "required_scope": "search:api_key",
                        "workaround": "配置API密钥或使用替代工具"
                    }
                ]
            },
            "web_fetch": {
                "description": "网页提取",
                "required_scopes": ["web:fetch"],
                "optional_scopes": [],
                "common_permission_issues": []
            },
            "read": {
                "description": "文件读取",
                "required_scopes": ["file:read"],
                "optional_scopes": [],
                "common_permission_issues": [
                    {
                        "issue": "文件不存在",
                        "required_scope": "file:read",
                        "workaround": "检查文件路径和权限"
                    }
                ]
            },
            "write": {
                "description": "文件写入",
                "required_scopes": ["file:write"],
                "optional_scopes": [],
                "common_permission_issues": []
            },
            "edit": {
                "description": "文件编辑",
                "required_scopes": ["file:write"],
                "optional_scopes": [],
                "common_permission_issues": []
            },
            "exec": {
                "description": "命令执行",
                "required_scopes": ["system:exec"],
                "optional_scopes": [],
                "common_permission_issues": [
                    {
                        "issue": "权限不足",
                        "required_scope": "system:exec",
                        "workaround": "使用sudo或调整权限"
                    }
                ]
            }
        }
    
    def load_scope_descriptions(self) -> Dict:
        """加载权限范围描述"""
        scopes_file = self.config_dir / "scope_descriptions.json"
        if scopes_file.exists():
            with open(scopes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认权限范围描述
        return {
            "docx:document:read_only": {
                "description": "读取飞书文档",
                "capabilities": ["读取文档内容", "查看文档信息", "列出文档块"],
                "limitations": ["不能修改文档", "不能创建新文档"],
                "typical_use": ["文档分析", "内容查看", "信息提取"]
            },
            "docx:document:write_only": {
                "description": "写入飞书文档",
                "capabilities": ["修改文档内容", "更新文档块", "添加内容"],
                "limitations": ["不能创建新文档", "需要文档已存在"],
                "typical_use": ["内容更新", "文档编辑", "批量修改"]
            },
            "docx:document:create": {
                "description": "创建飞书文档",
                "capabilities": ["创建新文档", "设置文档标题", "初始化内容"],
                "limitations": ["内容可能被写入标题", "需要两步操作添加正文"],
                "typical_use": ["文档创建", "报告生成", "内容初始化"]
            },
            "drive:drive:read_only": {
                "description": "读取飞书云存储",
                "capabilities": ["列出文件夹内容", "查看文件信息", "搜索文件"],
                "limitations": ["不能修改文件", "不能创建文件夹"],
                "typical_use": ["文件浏览", "内容搜索", "信息查看"]
            },
            "drive:drive:write_only": {
                "description": "写入飞书云存储",
                "capabilities": ["创建文件夹", "移动文件", "删除文件"],
                "limitations": ["不能读取文件内容", "需要文件已存在"],
                "typical_use": ["文件管理", "文件夹组织", "空间清理"]
            },
            "wiki:wiki:read_only": {
                "description": "读取飞书知识库",
                "capabilities": ["读取知识库内容", "搜索知识库", "查看节点信息"],
                "limitations": ["不能修改知识库", "不能创建节点"],
                "typical_use": ["知识检索", "内容查看", "信息学习"]
            },
            "wiki:wiki:write_only": {
                "description": "写入飞书知识库",
                "capabilities": ["创建知识库节点", "修改节点内容", "移动节点"],
                "limitations": ["需要知识库访问权限", "不能删除节点"],
                "typical_use": ["知识整理", "内容更新", "知识库维护"]
            },
            "search:web": {
                "description": "网页搜索",
                "capabilities": ["执行网页搜索", "获取搜索结果", "过滤搜索条件"],
                "limitations": ["需要API密钥", "有频率限制", "结果可能不完整"],
                "typical_use": ["信息搜索", "研究调查", "数据收集"]
            },
            "web:fetch": {
                "description": "网页提取",
                "capabilities": ["提取网页内容", "转换为markdown", "内容摘要"],
                "limitations": ["受网站限制", "可能被屏蔽", "需要网络连接"],
                "typical_use": ["内容采集", "信息提取", "网页分析"]
            },
            "file:read": {
                "description": "文件读取",
                "capabilities": ["读取文件内容", "查看文件信息", "文件搜索"],
                "limitations": ["需要文件存在", "需要读取权限", "受文件格式限制"],
                "typical_use": ["文件分析", "内容查看", "数据处理"]
            },
            "file:write": {
                "description": "文件写入",
                "capabilities": ["创建文件", "修改文件", "删除文件"],
                "limitations": ["需要写入权限", "可能覆盖现有文件", "受磁盘空间限制"],
                "typical_use": ["文件创建", "内容保存", "数据存储"]
            },
            "system:exec": {
                "description": "系统执行",
                "capabilities": ["执行命令", "运行脚本", "系统操作"],
                "limitations": ["需要执行权限", "可能有安全风险", "受系统限制"],
                "typical_use": ["自动化任务", "系统管理", "脚本执行"]
            }
        }
    
    def load_permission_hierarchy(self) -> Dict:
        """加载权限层级"""
        hierarchy_file = self.config_dir / "permission_hierarchy.json"
        if hierarchy_file.exists():
            with open(hierarchy_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认权限层级
        return {
            "docx": {
                "docx:document:all": {
                    "includes": ["docx:document:read_only", "docx:document:write_only", "docx:document:create"],
                    "description": "完整文档权限"
                },
                "docx:document:write": {
                    "includes": ["docx:document:write_only", "docx:document:create"],
                    "description": "文档写入权限"
                }
            },
            "drive": {
                "drive:drive:all": {
                    "includes": ["drive:drive:read_only", "drive:drive:write_only"],
                    "description": "完整云存储权限"
                }
            },
            "wiki": {
                "wiki:wiki:all": {
                    "includes": ["wiki:wiki:read_only", "wiki:wiki:write_only"],
                    "description": "完整知识库权限"
                }
            },
            "file": {
                "file:all": {
                    "includes": ["file:read", "file:write"],
                    "description": "完整文件权限"
                }
            },
            "system": {
                "system:all": {
                    "includes": ["system:exec", "system:process"],
                    "description": "完整系统权限"
                }
            }
        }
    
    def get_required_scopes(self, tool_name: str, action: str = None) -> List[str]:
        """
        获取工具操作所需的权限范围
        
        Args:
            tool_name: 工具名称
            action: 操作名称（可选）
            
        Returns:
            所需的权限范围列表
        """
        required_scopes = []
        
        # 1. 从工具需求获取基本范围
        if tool_name in self.tool_requirements:
            tool_req = self.tool_requirements[tool_name]
            required_scopes.extend(tool_req.get("required_scopes", []))
            
            if action:
                # 2. 从权限映射获取特定操作范围
                for category, tools in self.permission_mappings.items():
                    if tool_name in tools and action in tools[tool_name]:
                        required_scopes.extend(tools[tool_name][action])
        
        # 去重
        required_scopes = list(set(required_scopes))
        
        # 3. 扩展层级权限
        expanded_scopes = self.expand_hierarchical_scopes(required_scopes)
        
        return expanded_scopes
    
    def expand_hierarchical_scopes(self, scopes: List[str]) -> List[str]:
        """扩展层级权限"""
        expanded = set(scopes)
        
        for scope in scopes:
            # 检查是否是高级权限
            for category, hierarchy in self.permission_hierarchy.items():
                if scope in hierarchy:
                    # 这个scope本身是一个高级权限，需要展开
                    if "includes" in hierarchy[scope]:
                        expanded.update(hierarchy[scope]["includes"])
                else:
                    # 检查scope是否被某个高级权限包含
                    for parent_scope, parent_info in hierarchy.items():
                        if "includes" in parent_info and scope in parent_info["includes"]:
                            expanded.add(parent_scope)
        
        return list(expanded)
    
    def verify_permission(self, available_scopes: List[str], required_scopes: List[str]) -> Dict:
        """
        验证权限是否足够
        
        Args:
            available_scopes: 可用权限范围
            required_scopes: 所需权限范围
            
        Returns:
            验证结果
        """
        verification = {
            "available_scopes": available_scopes,
            "required_scopes": required_scopes,
            "missing_scopes": [],
            "satisfied_scopes": [],
            "hierarchical_matches": [],
            "coverage_percentage": 0.0,
            "verification_passed": False,
            "recommendations": []
        }
        
        available_set = set(available_scopes)
        required_set = set(required_scopes)
        
        # 检查直接匹配
        direct_matches = available_set.intersection(required_set)
        verification["satisfied_scopes"] = list(direct_matches)
        
        # 检查层级匹配
        hierarchical_matches = self.check_hierarchical_matches(available_scopes, required_scopes)
        verification["hierarchical_matches"] = hierarchical_matches
        
        # 计算缺失范围
        missing = required_set - available_set
        
        # 移除通过层级匹配满足的范围
        for match in hierarchical_matches:
            if match["required_scope"] in missing:
                missing.remove(match["required_scope"])
        
        verification["missing_scopes"] = list(missing)
        
        # 计算覆盖率
        total_required = len(required_set)
        satisfied = len(direct_matches) + len(hierarchical_matches)
        
        if total_required > 0:
            verification["coverage_percentage"] = (satisfied / total_required) * 100
        
        # 判断是否通过验证
        verification["verification_passed"] = len(verification["missing_scopes"]) == 0
        
        # 生成推荐
        verification["recommendations"] = self.generate_recommendations(
            verification["missing_scopes"],
            verification["hierarchical_matches"],
            verification["coverage_percentage"]
        )
        
        return verification
    
    def check_hierarchical_matches(self, available_scopes: List[str], required_scopes: List[str]) -> List[Dict]:
        """检查层级权限匹配"""
        matches = []
        
        for required_scope in required_scopes:
            for available_scope in available_scopes:
                # 检查available_scope是否包含required_scope
                if self.does_scope_include(available_scope, required_scope):
                    matches.append({
                        "available_scope": available_scope,
                        "required_scope": required_scope,
                        "relationship": "hierarchical_include",
                        "description": f"{available_scope} 包含 {required_scope}"
                    })
        
        return matches
    
    def does_scope_include(self, parent_scope: str, child_scope: str) -> bool:
        """检查父权限是否包含子权限"""
        # 直接相等
        if parent_scope == child_scope:
            return True
        
        # 检查权限层级
        for category, hierarchy in self.permission_hierarchy.items():
            if parent_scope in hierarchy:
                if "includes" in hierarchy[parent_scope]:
                    if child_scope in hierarchy[parent_scope]["includes"]:
                        return True
        
        return False
    
    def generate_recommendations(self, missing_scopes: List[str], hierarchical_matches: List[Dict], coverage_percentage: float) -> List[str]:
        """生成推荐"""
        recommendations = []
        
        # 缺失权限推荐
        for scope in missing_scopes:
            if scope in self.scope_descriptions:
                desc = self.scope_descriptions[scope]
                recommendations.append(f"申请权限: {scope} - {desc.get('description', '未知权限')}")
        
        # 层级匹配推荐
        if hierarchical_matches:
            recommendations.append("当前权限通过层级关系满足部分需求，但建议申请具体权限以获得最佳兼容性")
        
        # 覆盖率推荐
        if coverage_percentage < 100:
            recommendations.append(f"权限覆盖率为 {coverage_percentage:.1f}%，建议补充缺失权限")
        
        # 通用推荐
        if missing_scopes:
            recommendations.append("使用 feishu_app_scopes 工具查看当前权限范围")
            recommendations.append("联系管理员申请缺失权限")
        
        return recommendations
    
    def get_scope_description(self, scope: str) -> Dict:
        """获取权限范围描述"""
        if scope in self.scope_descriptions:
            return self.scope_descriptions[scope]
        
        return {
            "description": "未知权限范围",
            "capabilities": [],
            "limitations": ["权限信息不可用"],
            "typical_use": []
        }
    
    def format_verification_report(self, verification: Dict, tool_name: str = None, action: str = None) -> str:
        """格式化验证报告"""
        report = []
        report.append("=" * 70)
        report.append("LLM痛点分析器 - 智能权限验证报告")
        report.append("=" * 70)
        
        if tool_name:
            report.append(f"工具: {tool_name}")
        
        if action:
            report.append(f"操作: {action}")
        
        report.append(f"验证结果: {'通过' if verification['verification_passed'] else '失败'}")
        report.append(f"权限覆盖率: {verification['coverage_percentage']:.1f}%")
        report.append("-" * 70)
        
        # 所需权限
        if verification.get('required_scopes'):
            report.append("所需权限范围:")
            for scope in verification['required_scopes']:
                desc = self.get_scope_description(scope)
                report.append(f"  • {scope} - {desc.get('description', '未知')}")
        
        # 可用权限
        if verification.get('available_scopes'):
            report.append("\n可用权限范围:")
            for scope in verification['available_scopes']:
                desc = self.get_scope_description(scope)
                report.append(f"  • {scope} - {desc.get('description', '未知')}")
        
        # 满足的权限
        if verification.get('satisfied_scopes'):
            report.append("\n直接满足的权限:")
            for scope in verification['satisfied_scopes']:
                report.append(f"  ✓ {scope}")
        
        # 层级匹配
        if verification.get('hierarchical_matches'):
            report.append("\n层级关系满足的权限:")
            for match in verification['hierarchical_matches']:
                report.append(f"  ≈ {match['available_scope']} → {match['required_scope']}")
        
        # 缺失权限
        if verification.get('missing_scopes'):
            report.append("\n缺失的权限:")
            for scope in verification['missing_scopes']:
                desc = self.get_scope_description(scope)
                report.append(f"  ✗ {scope} - {desc.get('description', '未知')}")
        
        # 推荐
        if verification.get('recommendations'):
            report.append("\n推荐措施:")
            for i, rec in enumerate(verification['recommendations'], 1):
                report.append(f"  {i}. {rec}")
        
        report.append("=" * 70)
        return "\n".join(report)


def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description="LLM痛点分析器 - 权限验证模块")
    parser.add_argument("--tool", required=True, help="工具名称")
    parser.add_argument("--action", help="操作名称")
    parser.add_argument("--available-scopes", help="可用权限范围（JSON格式）")
    parser.add_argument("--config-dir", help="配置文件目录")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="输出格式")
    
    args = parser.parse_args()
    
    verifier = PermissionVerifier(args.config_dir)
    
    # 获取所需权限
    required_scopes = verifier.get_required_scopes(args.tool, args.action)
    
    # 解析可用权限
    available_scopes = []
    if args.available_scopes:
        try:
            available_scopes = json.loads(args.available_scopes)
        except json.JSONDecodeError:
            print("错误: 可用权限范围必须是有效的JSON格式")
            sys.exit(1)
    
    # 验证权限
    verification = verifier.verify_permission(available_scopes, required_scopes)
    
    if args.format == "json":
        print(json.dumps(verification, indent=2, ensure_ascii=False))
    else:
        print(verifier.format_verification_report(verification, args.tool, args.action))


if __name__ == "__main__":
    main()