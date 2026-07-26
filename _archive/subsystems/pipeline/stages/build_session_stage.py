"""BuildSessionStage - 初始化构建会话"""

from pipeline.stage import Stage


class BuildSessionStage(Stage):
    name = "Build Session"

    def run(self, context):
        session = context.session
        if session:
            print(f"  session_id : {session.session_id}")
            print(f"  output_dir : {context.output_dir}")
