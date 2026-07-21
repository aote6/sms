from .backend import Backend
from ir import IRModule, IRFunction

class RustBackend(Backend):
    name = "rust"
    extension = ".rs"
    
    def filename(self, ir: IRModule) -> str:
        return f"{ir.name.lower().replace(' ', '_')}{self.extension}"
    
    def emit(self, ir: IRModule) -> str:
        code = f'''// 由 SMS 生成
// 模块: {ir.name} v{ir.version}
// 后端: {self.name}

pub struct {ir.name.replace(' ', '')} {{
    version: String,
}}

impl {ir.name.replace(' ', '')} {{
    pub fn new() -> Self {{
        Self {{
            version: "{ir.version}".to_string(),
        }}
    }}
'''
        for fn in ir.functions:
            code += self._emit_function(fn)
        
        code += '''}

pub fn create() -> {name} {
    {name}::new()
}
'''.format(name=ir.name.replace(' ', ''))
        
        return code
    
    def _emit_function(self, fn: IRFunction) -> str:
        inputs = ", ".join(fn.inputs) if fn.inputs else ""
        code = f'''
    pub fn {fn.name}(&self, {inputs}) -> {fn.output} {{
        // TODO: 实现 {fn.name}
        unimplemented!()
    }}
'''
        return code
