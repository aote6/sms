"""Dominator Tree 构建 (迭代算法)"""


class DominatorTree:
    def build(self, graph, start):
        """构建支配树，返回 dom dict: node -> set(dominators)"""
        nodes = list(graph.nodes)

        # 初始化: 所有节点支配所有节点
        dom = {}
        for n in nodes:
            dom[n] = set(nodes)

        # start 只支配自己
        dom[start] = {start}

        changed = True
        while changed:
            changed = False
            for n in nodes:
                if n == start:
                    continue

                preds = graph.predecessors(n)
                if not preds:
                    continue

                # 交集: 所有前驱支配集的交集
                new = set(dom[preds[0]])
                for p in preds[1:]:
                    new &= dom[p]

                # 加上自己
                new.add(n)

                if new != dom[n]:
                    dom[n] = new
                    changed = True

        return dom

    def build_immediate(self, graph, start):
        """构建 immediate dominator (IDom)"""
        dom = self.build(graph, start)

        # 计算 IDom: 支配者中除了自己，被支配最多的那个
        idom = {}
        for n in dom:
            if n == start:
                idom[n] = None
                continue

            dominators = dom[n] - {n}
            if not dominators:
                idom[n] = None
                continue

            # 找最近支配者: 支配关系最深的那层
            # 简单实现: 找支配者中，其支配集最大的
            max_dom = None
            max_size = -1
            for d in dominators:
                if len(dom[d]) > max_size:
                    max_size = len(dom[d])
                    max_dom = d
            idom[n] = max_dom

        return idom

    def build_tree(self, graph, start):
        """构建支配树 (children dict)"""
        idom = self.build_immediate(graph, start)

        tree = {}
        for n in graph.nodes:
            tree[n] = set()

        for n, parent in idom.items():
            if parent is not None and n != start:
                tree[parent].add(n)

        return tree
