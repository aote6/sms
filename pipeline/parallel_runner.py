"""ParallelPipelineRunner - 并行流水线执行器（含 Profile）"""

from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from pipeline.context import PipelineContext
from pipeline.pipeline_dag import PipelineDAG
from pipeline.report import StageReport, PipelineProfile
import time


class ParallelPipelineRunner:
    def __init__(self, workers: int = 4, profile: bool = False):
        self.workers = workers
        self.profile_enabled = profile
        self.dag = PipelineDAG()
        self.profile = PipelineProfile()

    def add(self, stage):
        self.dag.add(stage)
        return self

    def depends_on(self, stage_name: str, *dep_names: str):
        self.dag.depends_on(stage_name, *dep_names)
        return self

    def run(self, ctx: PipelineContext):
        print()
        print("=" * 60)
        print("SMS Pipeline (Parallel DAG)")
        print("=" * 60)

        order = self.dag.topological_sort()
        print(f"  阶段: {len(order)} 个")
        print("=" * 60)

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {}
            completed = set()

            while not self.dag.all_done():
                for node in self.dag.ready_nodes():
                    if node.name not in completed:
                        future = executor.submit(self._run_node, node, ctx)
                        futures[future] = node
                        node.running = True

                if not futures:
                    break

                done, _ = wait(futures, return_when=FIRST_COMPLETED)

                for future in done:
                    node = futures.pop(future)
                    try:
                        report = future.result()
                        if report:
                            self.profile.add(report)
                        node.done = True
                        node.running = False
                        completed.add(node.name)
                    except Exception as e:
                        print(f"  ❌ {node.name} 失败: {e}")
                        raise

        self.dag.summary()

        if self.profile_enabled:
            self.profile.summary()
            self.profile.timeline()
            self.profile.slowest(3)

        print("✅ Pipeline 完成")
        print("=" * 60)

        # 保存 profile 到 ctx
        ctx.metadata["profile"] = self.profile
        return ctx

    def _run_node(self, node, ctx):
        """执行单个阶段并生成报告"""
        print(f"  ▶ {node.name}")
        start = time.perf_counter()
        status = "success"
        inputs = 0
        outputs = 0

        try:
            # 计算输入/输出（简化）
            if hasattr(node.stage, 'inputs'):
                inputs = len(node.stage.inputs(ctx))
            if hasattr(node.stage, 'outputs'):
                outputs = len(node.stage.outputs(ctx))

            node.stage.run(ctx)

            # 如果 stage 有成功标记，可以检查
            if hasattr(node.stage, 'failed') and node.stage.failed:
                status = "failed"

        except Exception as e:
            status = "failed"
            print(f"  ❌ {node.name} 失败: {e}")
            raise
        finally:
            end = time.perf_counter()

        print(f"  ✅ {node.name} 完成")
        return StageReport.create(
            name=node.name,
            start=start,
            end=end,
            status=status
        ).with_inputs(inputs).with_outputs(outputs)
