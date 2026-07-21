from pathlib import Path
from ir import IRModule, IRFunction
from build.artifact import Artifact
from .backend import Backend


class PythonBackend(Backend):
    name = "python"

    def __init__(self, output_dir: Path = Path("./dist")):
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

        has_main = any(fn.name == "main" for fn in ir.functions)
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
        if has_main:
            code += f'''    print("\\n执行 main 入口...")
    result = instance.main()
    print(f"结果: {{result}}")
'''
        return code

    def _clean_type(self, type_str: str) -> str:
        if not type_str or type_str in ("any", "none", "instance"):
            return "Any"
        if ": " in type_str:
            type_str = type_str.split(": ")[-1]
        elif ":" in type_str:
            type_str = type_str.split(":")[-1]
        return type_str.strip()

    def _emit_function(self, fn: IRFunction) -> str:
        inputs = []
        for inp in fn.inputs:
            if inp and inp not in ("none", "any"):
                if ": " in inp:
                    name, typ = inp.split(": ", 1)
                elif ":" in inp:
                    name, typ = inp.split(":", 1)
                else:
                    name, typ = inp, "Any"
                inputs.append(f"{name.strip()}: {typ.strip()}")
            elif inp and inp != "none":
                inputs.append(f"{inp}: Any")

        input_str = ", ".join(inputs) if inputs else ""
        output = self._clean_type(fn.output)

        code = f"    def {fn.name}(self, {input_str}) -> {output}:\n"
        if fn.doc:
            code += f'        """{fn.doc}"""\n'
        for line in fn.body:
            code += f"        {line}\n"
        code += "\n"
        return code
