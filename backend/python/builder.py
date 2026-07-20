import os
from ir import IRModule, IRFunction

class PythonBuilder:
    def __init__(self, output_dir="./build"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def build(self, ir: IRModule) -> str:
        filename = f"{self.output_dir}/{ir.name.lower().replace(' ', '_')}.py"
        
        with open(filename, 'w') as f:
            f.write(self._generate_code(ir))
        
        print(f"🔨 构建: {ir.name} → {filename}")
        return filename
    
    def _generate_code(self, ir: IRModule) -> str:
        code = f'''# 由 SMS IR 自动生成
# 模块: {ir.name} v{ir.version}
# 运行时: {ir.runtime}
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
            code += self._generate_function(fn, indent=4)
        
        code += f'''
def create():
    """工厂方法"""
    return {class_name}()

if __name__ == "__main__":
    instance = create()
    print(f"✅ {class_name} v{{instance.version}} 已加载")
'''
        return code
    
    def _generate_function(self, fn: IRFunction, indent: int = 4) -> str:
        spaces = " " * indent
        inputs = ", ".join(fn.inputs) if fn.inputs else ""
        code = f"{spaces}def {fn.name}(self, {inputs}) -> {fn.output}:\n"
        if fn.doc:
            code += f'{spaces}    """{fn.doc}"""\n'
        for line in fn.body:
            code += f"{spaces}    {line}\n"
        code += "\n"
        return code
