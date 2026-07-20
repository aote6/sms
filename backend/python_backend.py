from pathlib import Path
from ir import IRModule, IRFunction
from build.artifact import Artifact
from .backend import Backend

class PythonBackend(Backend):
    name = "python"
    
    def __init__(self, output_dir: Path = Path("./build")):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def emit(self, ir: IRModule) -> Artifact:
        filename = self.output_dir / f"{ir.name.lower().replace(' ', '_')}.py"
        code = self._generate(ir)
        filename.write_text(code, encoding="utf-8")
        print(f"🔨 构建: {filename}")
        return Artifact.create(
            module=ir.name,
            version=ir.version,
            language=self.name,
            path=filename
        )
    
    def _generate(self, ir: IRModule) -> str:
        code = f'''# 由 SMS 生成
# 模块: {ir.name} v{ir.version}
# 后端: {self.name}
# 能力: {ir.metadata.get('capabilities', [])}

'''
        for imp in ir.imports:
            code += f"{imp}\n"
        code += "\n"
        
        class_name = ir.name.replace(' ', '')
        code += f"class {class_name}:\n"
        code += f'    """{ir.name} 实现"""\n\n'
        
        code += "    def __init__(self):\n"
        code += f'        self.version = "{ir.version}"\n'
        code += "        self._initialized = True\n\n"
        
        for fn in ir.functions:
            code += self._emit_function(fn)
        
        code += f'''
def create():
    """工厂方法"""
    return {class_name}()

if __name__ == "__main__":
    instance = create()
    print(f"✅ {class_name} v{{instance.version}} 已加载")
'''
        return code
    
    def _emit_function(self, fn: IRFunction) -> str:
        inputs = ", ".join(fn.inputs) if fn.inputs else ""
        code = f"    def {fn.name}(self, {inputs}) -> {fn.output}:\n"
        if fn.doc:
            code += f'        """{fn.doc}"""\n'
        for line in fn.body:
            code += f"        {line}\n"
        code += "\n"
        return code
