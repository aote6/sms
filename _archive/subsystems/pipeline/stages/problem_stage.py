from pipeline.stage import Stage

class ProblemStage(Stage):
    name = "Problem Graph"

    def run(self, context):
        graph = context.get("graph")
        if graph:
            products = graph.products() if hasattr(graph, 'products') else []
            nodes = list(graph.nodes.keys()) if hasattr(graph, 'nodes') else []
            print(f"  products : {len(products)}")
            print(f"  nodes    : {len(nodes)}")
        else:
            print("  graph : None")
