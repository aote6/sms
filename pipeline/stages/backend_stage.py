"""BackendStage - 生成后端代码"""

from pipeline.stage import Stage


class BackendStage(Stage):
    name = "Backend"

    def run(self, context):
        if context.skip_build:
            print("  skip backend")
            return

        session = context.session
        backend = context.backend
        ir = context.ir

        if backend and ir:
            artifact = backend.emit(ir)
            context.artifact = artifact
            session.add_artifact(artifact)
            print(f"  artifact {artifact.path}")
        else:
            print("  (跳过)")
