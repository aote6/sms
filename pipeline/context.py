"""PipelineContext - 流水线上下文"""


class PipelineContext:
    def __init__(self):
        self.session = None
        self.graph = None
        self.module = None
        self.ir = None
        self.artifact = None
        self.package = None
        self.compiler = None
        self.backend = None
        self.packager = None
        self.planner = None
        self.resolver = None
        self.decision = None
        self.plan = None
        self.selected_decision = None
        self.build_context = None
        self.module_registry = None
        self.output_dir = "./build"
        self.cache = None
        self.skip_build = False
