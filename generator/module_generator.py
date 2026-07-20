import os
from core.node import NodeType
from core.module import Module

class ModuleGenerator:
    def __init__(self, output_dir="./generated"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, module: Module, node):
        if node.node_type != NodeType.MODULE:
            return
        
        filename = f"{self.output_dir}/{module.name.lower().replace(' ', '_')}.py"
        
        with open(filename, 'w') as f:
            f.write(self._generate_module_code(module))
        
        print(f"✓ 生成模块: {filename}")
        return filename
    
    def _generate_module_code(self, module: Module) -> str:
        class_name = module.name.replace(' ', '')
        cap_names = [c.name for c in module.capabilities]
        
        code = f'''"""
{module.name} v{module.version}
状态: {module.status.value}
约束: {', '.join(module.constraints) if module.constraints else '无'}
"""

class {class_name}:
    """自动生成的模块骨架"""
    
    def __init__(self):
        self.version = "{module.version}"
        self.capabilities = {cap_names}
'''
        
        for cap in module.capabilities:
            code += f'''
    def {cap.name}(self, {', '.join(cap.inputs) if cap.inputs else ''}):
        """{cap.description}
        输入: {', '.join(cap.inputs) if cap.inputs else '无'}
        输出: {', '.join(cap.outputs) if cap.outputs else '无'}
        """
        # TODO: 实现 {cap.name} 逻辑
        pass
'''
        
        code += f'''
if __name__ == "__main__":
    instance = {class_name}()
    print(f"{class_name} v{{instance.version}} 加载成功")
    print(f"能力: {{', '.join(instance.capabilities)}}")
'''
        return code
