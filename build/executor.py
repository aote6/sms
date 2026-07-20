"""BuildExecutor - 执行构建任务"""


class BuildExecutor:
    def __init__(
        self,
        registry,
        compiler,
        backend,
        packager,
        cache=None,
    ):
        self.registry = registry
        self.compiler = compiler
        self.backend = backend
        self.packager = packager
        self.cache = cache
        self.results = {}

    def build(self, node):
        module = self.registry.get(node.name)

        if module is None:
            print(f"  ⏭ {node.name} (无模块)")
            node.built = True
            node.dirty = False
            self.results[node.name] = None
            return None

        if self.cache:
            from build.fingerprint import Fingerprint
            fp = Fingerprint.module(module)
            old = self.cache.get(module.name)
            if old == fp:
                print(f"  ⏭ {node.name} (缓存命中)")
                node.built = True
                node.dirty = False
                self.results[node.name] = "cached"
                return "cached"

        print(f"  🔨 {module.name}")

        try:
            ir = self.compiler.compile(module)
            artifact = self.backend.emit(ir)
            package = self.packager.build(module.name, [artifact])

            if self.cache:
                from build.fingerprint import Fingerprint
                self.cache.put(module.name, Fingerprint.module(module))
                self.cache.save()

            node.built = True
            node.dirty = False

            # 存储路径字符串，而不是对象
            artifact_path = artifact.path if hasattr(artifact, 'path') else str(artifact)
            package_path = str(package) if package else None

            result = {
                "ir": ir,
                "artifact": artifact_path,
                "package": package_path,
            }
            self.results[node.name] = result
            return result

        except Exception as e:
            print(f"  ❌ {node.name} 构建失败: {e}")
            node.built = False
            self.results[node.name] = None
            raise

    def build_all(self, nodes):
        results = {}
        for node in nodes:
            results[node.name] = self.build(node)
        return results
