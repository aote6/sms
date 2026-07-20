import subprocess
from backend.python import PythonBuilder
from cache import BuildCache
from .runtime import Runtime

class PythonRuntime(Runtime):
    name = "python"
    
    def __init__(self):
        self.builder = PythonBuilder()
        self.cache = BuildCache()
    
    def build(self, ir):
        # 检查缓存
        if not self.cache.changed(ir.name, ir):
            print(f"⏭ 跳过 (未变化): {ir.name}")
            filename = f"{self.builder.output_dir}/{ir.name.lower().replace(' ', '_')}.py"
            return filename
        
        filename = self.builder.build(ir)
        return filename
    
    def run(self, filename):
        print(f"▶ 运行: {filename}")
        subprocess.run(
            ["python3", filename],
            check=False,
        )
