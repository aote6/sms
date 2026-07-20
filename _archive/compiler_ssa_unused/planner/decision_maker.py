"""Decision Maker - 根据问题做出决策"""

from core import Node, NodeType


class DecisionMaker:
    def decide(self, decision_node: Node, requirements: dict):
        """根据决策节点和需求生成决策"""
        decision = {
            "name": decision_node.name,
            "description": decision_node.data.get("description", ""),
            "approach": decision_node.data.get("approach", "default"),
            "requirements": requirements,
            "modules": [],
        }
        return decision
