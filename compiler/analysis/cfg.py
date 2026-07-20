"""Control Flow Graph 构建器"""

from .graph import Graph
from compiler.ir.instruction import Branch, Jump


class ControlFlowGraph:
    def build(self, fn):
        """从 IRFunction 构建 CFG"""
        graph = Graph()

        # 添加所有块
        for block in fn.blocks:
            graph.add_node(block.name)

        # 连接块
        for i, block in enumerate(fn.blocks):
            if not block.instructions:
                continue

            last = block.instructions[-1]

            if isinstance(last, Branch):
                graph.connect(block.name, last.true_block)
                graph.connect(block.name, last.false_block)

            elif isinstance(last, Jump):
                graph.connect(block.name, last.target)

            else:
                # Fallthrough: 下一个块
                if i + 1 < len(fn.blocks):
                    graph.connect(block.name, fn.blocks[i + 1].name)

        return graph

    def build_all(self, module):
        """为模块中所有函数构建 CFG"""
        return {fn.name: self.build(fn) for fn in module.functions}
