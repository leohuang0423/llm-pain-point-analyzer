#!/usr/bin/env python3
"""
LLM痛点分析器 - 错误诊断模块
解决API操作模式混淆问题
"""

import json
import sys
import re
import argparse
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import subprocess
from collections import defaultdict

class ErrorDiagnoser:
    """智能错误诊断器"""
    
    def __init__(self, config_dir: str = None):
        """初始化错误诊断器"""
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(__file__), "../config")
        
        self.config_dir = Path(config_dir)
        self.error_patterns = self.load_error_patterns()
        self.api_specs = self.load_api_specs()
        self.solution_templates = self.load_solution_templates()
        self.common_mistakes = self.load_common_mistakes()
        
    def load_error_patterns(self) -> Dict:
        """加载错误模式"""
        patterns_file = self.config_dir / "error_patterns.json"
        if patterns_file.exists():
            with open(patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认错误模式
        return {
            "permission_errors": {
                "patterns": [
                    r"permission.*denied",
                    r"access.*denied",
                    r"unauthorized",
                    r"forbidden",
                    r"scope.*required",
                    r"insufficient.*permission",
                    r"no.*permission"
                ],
                "category": "permission",
                "severity": "high",
                "common_tools": ["feishu_doc", "feishu_drive", "feishu_wiki", "web_search"]
            },
            "parameter_errors": {
                "patterns": [
                    r"invalid.*parameter",
                    r"missing.*parameter",
                    r"parameter.*required",
                    r"bad.*request",
                    r"400",
                    r"malformed.*request"
                ],
                "category": "parameter",
                "severity": "medium",
                "common_tools": ["feishu_doc", "feishu_drive", "feishu_wiki", "web_search", "web_fetch"]
            },
            "api_errors": {
                "patterns": [
                    r"api.*error",
                    r"internal.*error",
                    r"500",
                    r"server.*error",
                    r"timeout",
                    r"connection.*failed"
                ],
                "category": "api",
                "severity": "high",
                "common_tools": ["all"]
            },
            "rate_limit_errors": {
                "patterns": [
                    r"rate.*limit",
                    r"too.*many.*requests",
                    r"429",
                    r"quota.*exceeded"
                ],
                "category": "rate_limit",
                "severity": "medium",
                "common_tools": ["web_search", "feishu_doc", "feishu_drive"]
            },
            "not_found_errors": {
                "patterns": [
                    r"not.*found",
                    r"404",
                    r"file.*not.*found",
                    r"resource.*not.*found"
                ],
                "category": "not_found",
                "severity": "low",
                "common_tools": ["read", "write", "feishu_doc", "feishu_drive"]
            },
            "validation_errors": {
                "patterns": [
                    r"validation.*failed",
                    r"invalid.*format",
                    r"type.*error",
                    r"value.*error"
                ],
                "category": "validation",
                "severity": "medium",
                "common_tools": ["feishu_doc", "feishu_wiki", "web_fetch"]
            }
        }
    
    def load_api_specs(self) -> Dict:
        """加载API规格"""
        specs_file = self.config_dir / "api_specs.json"
        if specs_file.exists():
            with open(specs_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认API规格
        return {
            "feishu_doc": {
                "create": {
                    "description": "创建飞书文档",
                    "required_params": ["title"],
                    "optional_params": ["content", "folder_token"],
                    "common_mistakes": [
                        {
                            "mistake": "将content参数内容写入标题",
                            "symptom": "文档标题显示完整内容",
                            "cause": "API设计缺陷，content参数被写入标题属性",
                            "solution": "使用两步操作：1) 创建只有标题的文档 2) 使用update_block添加正文"
                        }
                    ],
                    "error_messages": {
                        "400": "参数错误或权限不足",
                        "403": "没有写入权限",
                        "500": "服务器内部错误"
                    }
                },
                "read": {
                    "description": "读取飞书文档",
                    "required_params": ["doc_token"],
                    "optional_params": [],
                    "error_messages": {
                        "403": "没有读取权限",
                        "404": "文档不存在"
                    }
                },
                "update_block": {
                    "description": "更新文档块内容",
                    "required_params": ["doc_token", "block_id", "content"],
                    "optional_params": [],
                    "error_messages": {
                        "400": "block_id无效或内容格式错误",
                        "403": "没有写入权限",
                        "404": "文档或块不存在"
                    }
                }
            },
            "feishu_drive": {
                "list": {
                    "description": "列出文件夹内容",
                    "required_params": ["folder_token"],
                    "optional_params": ["type"],
                    "error_messages": {
                        "403": "没有读取权限",
                        "404": "文件夹不存在"
                    }
                },
                "create_folder": {
                    "description": "创建文件夹",
                    "required_params": ["name"],
                    "optional_params": ["folder_token"],
                    "error_messages": {
                        "400": "名称无效或已存在",
                        "403": "没有写入权限"
                    }
                }
            },
            "web_search": {
                "search": {
                    "description": "网页搜索",
                    "required_params": ["query"],
                    "optional_params": ["count", "country", "freshness"],
                    "common_mistakes": [
                        {
                            "mistake": "API密钥未配置",
                            "symptom": "搜索失败，无结果返回",
                            "cause": "Brave Search API需要API密钥",
                            "solution": "配置API密钥或使用替代搜索工具"
                        }
                    ],
                    "error_messages": {
                        "401": "API密钥无效",
                        "429": "请求频率过高",
                        "500": "搜索服务内部错误"
                    }
                }
            },
            "web_fetch": {
                "fetch": {
                    "description": "提取网页内容",
                    "required_params": ["url"],
                    "optional_params": ["extract_mode", "max_chars"],
                    "error_messages": {
                        "400": "URL无效",
                        "404": "网页不存在",
                        "429": "请求频率过高",
                        "500": "提取服务内部错误"
                    }
                }
            }
        }
    
    def load_solution_templates(self) -> Dict:
        """加载解决方案模板"""
        templates_file = self.config_dir / "solution_templates.json"
        if templates_file.exists():
            with open(templates_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认解决方案模板
        return {
            "permission": {
                "immediate": [
                    "检查当前权限范围",
                    "使用feishu_app_scopes工具查看可用权限",
                    "验证所需权限是否在可用权限列表中"
                ],
                "short_term": [
                    "联系管理员添加所需权限",
                    "申请权限范围扩展",
                    "使用替代工具或方法"
                ],
                "long_term": [
                    "建立权限需求文档",
                    "自动化权限验证流程",
                    "实施权限预检系统"
                ]
            },
            "parameter": {
                "immediate": [
                    "检查参数名称和格式",
                    "验证必填参数是否提供",
                    "检查参数值是否符合要求"
                ],
                "short_term": [
                    "查看API文档确认参数要求",
                    "使用示例代码验证参数格式",
                    "尝试简化参数组合"
                ],
                "long_term": [
                    "建立参数验证库",
                    "实施参数预检系统",
                    "创建参数模板系统"
                ]
            },
            "api": {
                "immediate": [
                    "检查网络连接",
                    "重试操作",
                    "验证API端点可用性"
                ],
                "short_term": [
                    "查看API状态页面",
                    "联系技术支持",
                    "使用备用API端点"
                ],
                "long_term": [
                    "实施API监控系统",
                    "建立故障转移机制",
                    "创建API健康检查"
                ]
            },
            "rate_limit": {
                "immediate": [
                    "等待一段时间后重试",
                    "减少请求频率",
                    "批量处理请求"
                ],
                "short_term": [
                    "申请API配额提升",
                    "优化请求策略",
                    "使用缓存减少请求"
                ],
                "long_term": [
                    "实施请求队列系统",
                    "建立智能节流机制",
                    "创建分布式请求处理"
                ]
            },
            "not_found": {
                "immediate": [
                    "检查资源ID或路径",
                    "验证资源是否存在",
                    "确认访问权限"
                ],
                "short_term": [
                    "使用搜索功能查找资源",
                    "检查资源是否被移动或删除",
                    "创建缺失的资源"
                ],
                "long_term": [
                    "实施资源验证系统",
                    "建立资源索引",
                    "创建资源同步机制"
                ]
            },
            "validation": {
                "immediate": [
                    "检查数据格式",
                    "验证数据类型",
                    "确认数据范围"
                ],
                "short_term": [
                    "查看数据格式要求",
                    "使用数据验证工具",
                    "清理和格式化数据"
                ],
                "long_term": [
                    "建立数据验证库",
                    "实施数据预处理系统",
                    "创建数据质量监控"
                ]
            }
        }
    
    def load_common_mistakes(self) -> Dict:
        """加载常见错误"""
        mistakes_file = self.config_dir / "common_mistakes.json"
        if mistakes_file.exists():
            with open(mistakes_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # 默认常见错误
        return {
            "feishu_doc_create": {
                "description": "feishu_doc.create操作将内容写入标题",
                "error_message": "文档创建成功但标题显示完整内容",
                "root_cause": "API设计缺陷，content参数被写入标题属性",
                "solution": "使用两步操作：1) feishu_doc.create(title='标题', content='标题') 2) feishu_doc.update_block(doc_token=doc_id, block_id=doc_id, content='正文内容')",
                "prevention": "创建文档时只提供标题，使用update_block添加正文"
            },
            "web_search_no_api_key": {
                "description": "web_search工具需要API密钥",
                "error_message": "搜索失败，API密钥未配置",
                "root_cause": "Brave Search API需要配置API密钥",
                "solution": "1) 申请Brave Search API密钥 2) 配置环境变量 3) 使用替代搜索工具如DuckDuckGo",
                "prevention": "提前配置所有需要的API密钥，建立密钥管理系统"
            },
            "permission_assumption": {
                "description": "假设拥有权限但实际没有",
                "error_message": "权限不足，操作被拒绝",
                "root_cause": "权限认知偏差，未验证实际权限",
                "solution": "1) 使用feishu_app_scopes查看当前权限 2) 验证所需权限 3) 申请缺失权限",
                "prevention": "实施权限预检系统，操作前自动验证权限"
            },
            "parameter_format": {
                "description": "参数格式不正确",
                "error_message": "参数无效或格式错误",
                "root_cause": "未遵循API参数格式要求",
                "solution": "1) 查看API文档 2) 使用正确格式 3) 验证参数类型",
                "prevention": "建立参数验证库，实施参数预检"
            }
        }
    
    def diagnose_error(self, error_message: str, tool_name: str = None, action: str = None, context: Dict = None) -> Dict:
        """
        诊断错误
        
        Args:
            error_message: 错误信息
            tool_name: 工具名称
            action: 操作名称
            context: 上下文信息
            
        Returns:
            错误诊断结果
        """
        diagnosis = {
            "error_message": error_message,
            "tool": tool_name,
            "action": action,
            "error_category": "unknown",
            "error_type": "unknown",
            "matched_patterns": [],
            "severity": "unknown",
            "root_cause": "未知",
            "immediate_solutions": [],
            "short_term_solutions": [],
            "long_term_solutions": [],
            "prevention_measures": [],
            "confidence": 0.0,
            "related_common_mistakes": []
        }
        
        # 1. 模式匹配
        matched_categories = self.match_error_patterns(error_message)
        diagnosis["matched_patterns"] = matched_categories
        
        if matched_categories:
            # 使用第一个匹配的类别
            primary_category = matched_categories[0]["category"]
            diagnosis["error_category"] = primary_category
            diagnosis["error_type"] = matched_categories[0].get("type", "unknown")
            diagnosis["severity"] = matched_categories[0].get("severity", "unknown")
            diagnosis["confidence"] = matched_categories[0].get("confidence", 0.0)
        
        # 2. 工具特定分析
        if tool_name and action:
            tool_specific = self.analyze_tool_specific_error(tool_name, action, error_message, context)
            diagnosis.update(tool_specific)
        
        # 3. 常见错误匹配
        common_mistakes = self.match_common_mistakes(error_message, tool_name, action)
        diagnosis["related_common_mistakes"] = common_mistakes
        
        if common_mistakes:
            # 使用第一个常见错误的信息
            mistake = common_mistakes[0]
            diagnosis["root_cause"] = mistake.get("root_cause", diagnosis["root_cause"])
            diagnosis["immediate_solutions"].extend(mistake.get("immediate_solutions", []))
            diagnosis["prevention_measures"].extend(mistake.get("prevention_measures", []))
        
        # 4. 生成解决方案
        solutions = self.generate_solutions(diagnosis["error_category"], tool_name, action, context)
        diagnosis["immediate_solutions"].extend(solutions.get("immediate", []))
        diagnosis["short_term_solutions"].extend(solutions.get("short_term", []))
        diagnosis["long_term_solutions"].extend(solutions.get("long_term", []))
        
        # 5. 去重解决方案
        diagnosis["immediate_solutions"] = list(set(diagnosis["immediate_solutions"]))
        diagnosis["short_term_solutions"] = list(set(diagnosis["short_term_solutions"]))
        diagnosis["long_term_solutions"] = list(set(diagnosis["long_term_solutions"]))
        diagnosis["prevention_measures"] = list(set(diagnosis["prevention_measures"]))
        
        return diagnosis
    
    def match_error_patterns(self, error_message: str) -> List[Dict]:
        """匹配错误模式"""
        matches = []
        error_lower = error_message.lower()
        
        for category_name, category_info in self.error_patterns.items():
            patterns = category_info.get("patterns", [])
            
            for pattern in patterns:
                if re.search(pattern, error_lower, re.IGNORECASE):
                    confidence = 1.0
                    
                    # 根据匹配强度调整置信度
                    if re.search(pattern.replace(".*", ""), error_lower, re.IGNORECASE):
                        confidence = 0.9
                    else:
                        # 部分匹配
                        matched_words = re.findall(r'\b\w+\b', pattern)
                        if any(word in error_lower for word in matched_words):
                            confidence = 0.7
                    
                    matches.append({
                        "category": category_info.get("category", category_name),
                        "type": category_name,
                        "severity": category_info.get("severity", "unknown"),
                        "pattern": pattern,
                        "confidence": confidence,
                        "common_tools": category_info.get("common_tools", [])
                    })
                    break  # 每个类别只匹配第一个模式
        
        # 按置信度排序
        matches.sort(key=lambda x: x["confidence"], reverse=True)
        return matches
    
    def analyze_tool_specific_error(self, tool_name: str, action: str, error_message: str, context: Dict = None) -> Dict:
        """分析工具特定错误"""
        result = {
            "tool_specific_analysis": {},
            "api_spec_violations": [],
            "parameter_issues": []
        }
        
        # 检查API规格
        if tool_name in self.api_specs and action in self.api_specs[tool_name]:
            api_spec = self.api_specs[tool_name][action]
            
            # 检查错误消息
            error_messages = api_spec.get("error_messages", {})
            for code, description in error_messages.items():
                if code in error_message or description.lower() in error_message.lower():
                    result["tool_specific_analysis"]["error_code"] = code
                    result["tool_specific_analysis"]["error_description"] = description
            
            # 检查常见错误
            common_mistakes = api_spec.get("common_mistakes", [])
            for mistake in common_mistakes:
                if mistake.get("symptom", "").lower() in error_message.lower():
                    result["tool_specific_analysis"]["common_mistake"] = mistake
        
        # 分析参数问题
        if "parameter" in error_message.lower() or "invalid" in error_message.lower():
            result["parameter_issues"].append("检查参数名称和格式")
            result["parameter_issues"].append("验证必填参数是否提供")
        
        return result
    
    def match_common_mistakes(self, error_message: str, tool_name: str = None, action: str = None) -> List[Dict]:
        """匹配常见错误"""
        matches = []
        error_lower = error_message.lower()
        
        for mistake_id, mistake_info in self.common_mistakes.items():
            # 检查工具匹配
            if tool_name:
                tool_part = mistake_id.split("_")[0]
                if tool_name != tool_part and tool_part != "permission" and tool_part != "parameter":
                    continue
            
            # 检查错误消息匹配
            if mistake_info.get("error_message", "").lower() in error_lower:
                matches.append({
                    "id": mistake_id,
                    "description": mistake_info.get("description", ""),
                    "root_cause": mistake_info.get("root_cause", ""),
                    "immediate_solutions": [mistake_info.get("solution", "")],
                    "prevention_measures": [mistake_info.get("prevention", "")]
                })
        
        return matches
    
    def generate_solutions(self, error_category: str, tool_name: str = None, action: str = None, context: Dict = None) -> Dict:
        """生成解决方案"""
        solutions = {
            "immediate": [],
            "short_term": [],
            "long_term": []
        }
        
        # 基于错误类别的通用解决方案
        if error_category in self.solution_templates:
            category_solutions = self.solution_templates[error_category]
            solutions["immediate"].extend(category_solutions.get("immediate", []))
            solutions["short_term"].extend(category_solutions.get("short_term", []))
            solutions["long_term"].extend(category_solutions.get("long_term", []))
        
        # 工具特定的解决方案
        if tool_name and action:
            tool_specific = self.get_tool_specific_solutions(tool_name, action, error_category)
            solutions["immediate"].extend(tool_specific.get("immediate", []))
            solutions["short_term"].extend(tool_specific.get("short_term", []))
            solutions["long_term"].extend(tool_specific.get("long_term", []))
        
        return solutions
    
    def get_tool_specific_solutions(self, tool_name: str, action: str, error_category: str) -> Dict:
        """获取工具特定解决方案"""
        solutions = {
            "immediate": [],
            "short_term": [],
            "long_term": []
        }
        
        # 飞书文档特定解决方案
        if tool_name == "feishu_doc" and action == "create" and error_category == "parameter":
            solutions["immediate"].append("使用两步操作创建文档：1) 创建标题 2) 使用update_block添加内容")
            solutions["short_term"].append("创建文档创建模板函数")
            solutions["long_term"].append("向飞书API团队反馈此设计缺陷")
        
        # 搜索工具特定解决方案
        if tool_name == "web_search" and error_category == "permission":
            solutions["immediate"].append("检查Brave Search API密钥配置")
            solutions["short_term"].append("使用DuckDuckGo等替代搜索工具")
            solutions["long_term"].append("建立统一的API密钥管理系统")
        
        # 权限相关解决方案
        if error_category == "permission":
            solutions["immediate"].append(f"使用feishu_app_scopes检查{tool_name}的当前权限")
            solutions["short_term"].append(f"申请{tool_name}.{action}所需的权限范围")
            solutions["long_term"].append("实施权限预检和自动验证系统")
        
        return solutions
    
    def format_diagnosis_report(self, diagnosis: Dict) -> str:
        """格式化诊断报告"""
        report = []
        report.append("=" * 70)
        report.append("LLM痛点分析器 - 智能错误诊断报告")
        report.append("=" * 70)
        report.append(f"错误信息: {diagnosis.get('error_message', '未知错误')}")
        
        if diagnosis.get('tool'):
            report.append(f"工具: {diagnosis['tool']}")
        
        if diagnosis.get('action'):
            report.append(f"操作: {diagnosis['action']}")
        
        report.append(f"错误类别: {diagnosis.get('error_category', '未知')}")
        report.append(f"严重程度: {diagnosis.get('severity', '未知')}")
        report.append(f"诊断置信度: {diagnosis.get('confidence', 0.0)*100:.1f}%")
        report.append("-" * 70)
        
        # 根本原因
        if diagnosis.get('root_cause') and diagnosis['root_cause'] != '未知':
            report.append("根本原因:")
            report.append(f"  {diagnosis['root_cause']}")
        
        # 匹配的模式
        if diagnosis.get('matched_patterns'):
            report.append("\n匹配的错误模式:")
            for match in diagnosis['matched_patterns'][:3]:
                report.append(f"  • {match.get('type', '未知')} (置信度: {match.get('confidence', 0.0)*100:.1f}%)")
        
        # 常见错误
        if diagnosis.get('related_common_mistakes'):
            report.append("\n相关常见错误:")
            for mistake in diagnosis['related_common_mistakes'][:2]:
                report.append(f"  • {mistake.get('description', '未知')}")
        
        # 立即解决方案
        if diagnosis.get('immediate_solutions'):
            report.append("\n立即解决方案:")
            for i, solution in enumerate(diagnosis['immediate_solutions'][:5], 1):
                report.append(f"  {i}. {solution}")
        
        # 短期解决方案
        if diagnosis.get('short_term_solutions'):
            report.append("\n短期解决方案 (1-7天):")
            for i, solution in enumerate(diagnosis['short_term_solutions'][:3], 1):
                report.append(f"  {i}. {solution}")
        
        # 长期解决方案
        if diagnosis.get('long_term_solutions'):
            report.append("\n长期解决方案 (1-4周):")
            for i, solution in enumerate(diagnosis['long_term_solutions'][:2], 1):
                report.append(f"  {i}. {solution}")
        
        # 预防措施
        if diagnosis.get('prevention_measures'):
            report.append("\n预防措施:")
            for i, measure in enumerate(diagnosis['prevention_measures'][:3], 1):
                report.append(f"  {i}. {measure}")
        
        report.append("=" * 70)
        return "\n".join(report)


def main():
    """命令行入口点"""
    parser = argparse.ArgumentParser(description="LLM痛点分析器 - 错误诊断模块")
    parser.add_argument("error", help="错误信息")
    parser.add_argument("--tool", help="工具名称")
    parser.add_argument("--action", help="操作名称")
    parser.add_argument("--config-dir", help="配置文件目录")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="输出格式")
    
    args = parser.parse_args()
    
    diagnoser = ErrorDiagnoser(args.config_dir)
    
    # 诊断错误
    diagnosis = diagnoser.diagnose_error(args.error, args.tool, args.action)
    
    if args.format == "json":
        print(json.dumps(diagnosis, indent=2, ensure_ascii=False))
    else:
        print(diagnoser.format_diagnosis_report(diagnosis))


if __name__ == "__main__":
    main()