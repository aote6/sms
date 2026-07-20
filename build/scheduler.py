from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Any
from assembly import AssemblyPlan

class Scheduler:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def schedule(self, plan: AssemblyPlan, task_fn: Callable[[Any], Any]) -> List[Any]:
        """
        按拓扑序调度任务，并行执行
        task_fn: 接收节点，返回结果
        """
        results = []
        futures = {}
        
        # 获取拓扑序
        sorted_nodes = plan.topological_sort()
        
        # 提交所有任务（按拓扑序，但执行是并行的）
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_node = {
                executor.submit(task_fn, node): node 
                for node in sorted_nodes
            }
            
            for future in as_completed(future_to_node):
                node = future_to_node[future]
                try:
                    result = future.result()
                    results.append((node, result))
                except Exception as e:
                    results.append((node, f"ERROR: {e}"))
        
        return results
    
    def shutdown(self):
        self.executor.shutdown(wait=True)
