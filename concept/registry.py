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

        # 自动添加到父类的 children 列表
        if concept.parent and concept.parent in self._by_id:
            parent = self._by_id[concept.parent]
            if concept.concept_id not in parent.children:
                parent.children.append(concept.concept_id)

    def get(self, concept_id: str) -> Optional[Concept]:
        """按ID查找"""
        return self._by_id.get(concept_id)

    def find(self, name: str) -> Optional[Concept]:
        """按名称或别名查找"""
        concept_id = self._by_alias.get(name.lower())
        if concept_id:
            return self._by_id.get(concept_id)
        for alias, cid in self._by_alias.items():
            if name.lower() in alias or alias in name.lower():
                return self._by_id.get(cid)
        return None

    def resolve(self, name: str) -> Optional[str]:
        """给定一个名称，返回对应的概念ID"""
        concept = self.find(name)
        return concept.concept_id if concept else None

    def list_all(self) -> List[Concept]:
        return list(self._by_id.values())

    def children_of(self, parent_id: str) -> List[Concept]:
        """获取某个概念的所有子概念"""
        parent = self.get(parent_id)
        if parent is None:
            return []
        return [self._by_id[cid] for cid in parent.children if cid in self._by_id]
