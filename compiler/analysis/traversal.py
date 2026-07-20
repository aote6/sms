"""图遍历算法: DFS, Reverse Post Order"""


class Traversal:
    @staticmethod
    def dfs(graph, start):
        """深度优先遍历"""
        visited = set()
        order = []

        def visit(node):
            if node in visited:
                return
            visited.add(node)
            order.append(node)
            for nxt in graph.successors(node):
                visit(nxt)

        visit(start)
        return order

    @staticmethod
    def reverse_post_order(graph, start):
        """Reverse Post Order (RPO)"""
        visited = set()
        post = []

        def visit(node):
            if node in visited:
                return
            visited.add(node)
            for nxt in graph.successors(node):
                visit(nxt)
            post.append(node)

        visit(start)
        post.reverse()
        return post

    @staticmethod
    def reachable(graph, start):
        """从 start 可达的所有节点"""
        visited = set()

        def visit(node):
            if node in visited:
                return
            visited.add(node)
            for nxt in graph.successors(node):
                visit(nxt)

        visit(start)
        return visited
