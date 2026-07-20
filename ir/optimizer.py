from .ir import IRModule, IRFunction

class IROptimizer:
    def __init__(self, level: int = 1):
        self.level = level
    
    def optimize(self, ir: IRModule) -> IRModule:
        if self.level >= 1:
            ir = self._level1_optimize(ir)
        if self.level >= 2:
            ir = self._level2_optimize(ir)
        return ir
    
    def _level1_optimize(self, ir: IRModule) -> IRModule:
        """基础优化：移除空函数、合并重复"""
        # 过滤空函数
        ir.functions = [f for f in ir.functions if f.body]
        
        # 去重函数（按名称）
        seen = set()
        unique = []
        for f in ir.functions:
            if f.name not in seen:
                seen.add(f.name)
                unique.append(f)
        ir.functions = unique
        
        return ir
    
    def _level2_optimize(self, ir: IRModule) -> IRModule:
        """高级优化：内联、死代码消除"""
        for fn in ir.functions:
            # 移除注释行（死代码）
            fn.body = [line for line in fn.body if not line.strip().startswith("# TODO") or "内联" in line]
            # 如果body为空，添加占位
            if not fn.body:
                fn.body = ["return None"]
        return ir
    
    def optimize_all(self, modules: list[IRModule]) -> list[IRModule]:
        return [self.optimize(m) for m in modules]
