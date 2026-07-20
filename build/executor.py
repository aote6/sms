"""BuildExecutor - 执行构建任务（支持 CacheEntry）"""

import time
from build.cache_entry import CacheEntry
from build.fingerprint import Fingerprint


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

        # 计算指纹
        fp = Fingerprint.module(module)

        # 检查缓存
        if self.cache:
            entry = self.cache.get(module.name)
            if entry and entry.fingerprint == fp:
                print(f"  ⏭ {node.name} (缓存命中)")
                node.built = True
                node.dirty = False
                self.results[node.name] = {
                    "cached": True,
                    "artifact": entry.artifact,
                    "abi": entry.abi,
                    "package": entry.package,
                }
                return self.results[node.name]

        print(f"  🔨 {module.name}")

        try:
            ir = self.compiler.compile(module)
            artifact = self.backend.emit(ir)
            package = self.packager.build(module.name, [artifact])

            # 获取路径
            artifact_path = artifact.path if hasattr(artifact, 'path') else str(artifact)
            package_path = str(package) if package else None

            # 保存到缓存
            if self.cache:
                entry = CacheEntry(
                    module=module.name,
                    fingerprint=fp,
                    artifact=artifact_path,
                    abi="",  # 暂未生成 ABI
                    package=package_path,
                    timestamp=time.time(),
                )
                self.cache.put(entry)
                self.cache.save()

            node.built = True
            node.dirty = False

            result = {
                "cached": False,
                "ir": ir,
                "artifact": artifact_path,
                "package": package_path,
                "fingerprint": fp,
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
