"""Control Flow Graph 构建器"""

from .graph import Graph
from compiler.instructions import Branch, Jump
from compiler.ir.instruction import Return


class ControlFlowGraph:
    def build(self, fn):
        graph = Graph()

        for block in fn.blocks:
            graph.add_node(block.name)

        for i, block in enumerate(fn.blocks):
            if not block.instructions:
                continue

            last = block.instructions[-1]

            if isinstance(last, Branch):
                graph.connect(block.name, last.true_block)
                graph.connect(block.name, last.false_block)

            elif isinstance(last, Jump):
                graph.connect(block.name, last.target)

            elif isinstance(last, Return):
                # Return 是终止指令，没有后继
                pass

            else:
                if i + 1 < len(fn.blocks):
                    graph.connect(block.name, fn.blocks[i + 1].name)

        return graph

    def build_all(self, module):
        return {fn.name: self.build(fn) for fn in module.functions}
