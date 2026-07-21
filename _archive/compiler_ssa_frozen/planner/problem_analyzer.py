"""Problem Analyzer - 分析问题并生成需求"""

from core import Node, NodeType


class ProblemAnalyzer:
    def analyze(self, problem_node: Node):
        """分析问题节点，提取需求"""
        requirements = {
            "name": problem_node.name,
            "description": problem_node.data.get("description", ""),
            "type": problem_node.data.get("type", "unknown"),
            "constraints": problem_node.data.get("constraints", []),
        }
        return requirements
