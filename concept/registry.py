from typing import Optional, List
from .concept import Concept


class ConceptRegistry:
    """能力概念注册表（型号目录）"""

    def __init__(self):
        self._by_id: dict[str, Concept] = {}
        self._by_alias: dict[str, str] = {}

    def register(self, concept: Concept):
        """注册一个新概念，自动建立父子关系"""
        self._by_id[concept.concept_id] = concept
        self._by_alias[concept.name.lower()] = concept.concept_id
        for alias in concept.aliases:
            self._by_alias[alias.lower()] = concept.concept_id

        if concept.parent and concept.parent in self._by_id:
            parent = self._by_id[concept.parent]
            if concept.concept_id not in parent.children:
                parent.children.append(concept.concept_id)

    def get(self, concept_id: str) -> Optional[Concept]:
        return self._by_id.get(concept_id)

    def find(self, name: str) -> Optional[Concept]:
        """按名称或别名查找，支持模糊匹配"""
        if not name:
            return None

        key = name.lower().replace('_', '').replace('-', '').replace(' ', '')

        # 1. 精确匹配
        concept_id = self._by_alias.get(name.lower())
        if concept_id:
            return self._by_id.get(concept_id)

        # 2. 标准化后匹配（去掉下划线、连字符、空格）
        for alias, cid in self._by_alias.items():
            normalized = alias.lower().replace('_', '').replace('-', '').replace(' ', '')
            if key == normalized:
                return self._by_id.get(cid)

        # 3. 包含匹配
        for alias, cid in self._by_alias.items():
            if key in alias or alias in key:
                return self._by_id.get(cid)

        return None

    def resolve(self, name: str) -> Optional[str]:
        concept = self.find(name)
        return concept.concept_id if concept else None

    def list_all(self) -> List[Concept]:
        return list(self._by_id.values())

    def children_of(self, parent_id: str) -> List[Concept]:
        parent = self.get(parent_id)
        if parent is None:
            return []
        return [self._by_id[cid] for cid in parent.children if cid in self._by_id]
