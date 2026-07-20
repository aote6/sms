"""PackageStage - 打包成 .smspkg"""

from pipeline.stage import Stage


class PackageStage(Stage):
    name = "Package"

    def run(self, context):
        if context.skip_build:
            print("  skip package")
            return

        session = context.session
        packager = context.packager
        artifacts = session.artifacts

        if packager and artifacts:
            module_name = "Unknown"
            if session.modules:
                module_name = session.modules[0].name

            package = packager.build(module_name, artifacts)
            context.package = package
            session.add_package(package)
            print(f"  package {package}")
        else:
            print("  (跳过)")
