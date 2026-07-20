"""Inline - 函数内联（SSA 值直接映射 + 命名空间隔离）"""

from compiler.passes.base import Pass
from compiler.passes.inline_mapper import InlineMapper
from compiler.ssa_core import SSAValueGenerator


class Inline(Pass):
    name = "Inline"

    def run(self, module):
        print(f"⚙ Pass: {self.name}")

        funcs = {f.name: f for f in module.functions}
        count = 0

        for fn in module.functions:
            # 计算当前函数中已使用的最大 SSA 值 ID
            max_id = -1
            for block in fn.blocks:
                for inst in block.instructions:
                    if hasattr(inst, 'result') and hasattr(inst.result, 'id'):
                        max_id = max(max_id, inst.result.id)

            # 从 max_id + 1 开始生成新值
            value_gen = SSAValueGenerator(start=max_id + 1)

            for block in fn.blocks:
                new_instructions = []
                result_map = {}
                inline_results = {}

                for inst in block.instructions:
                    if type(inst).__name__ != "Call":
                        new_instructions.append(inst)
                        continue

                    callee = funcs.get(inst.fn_name)
                    if callee is None:
                        new_instructions.append(inst)
                        continue

                    if len(callee.blocks) != 1 or len(callee.blocks[0].instructions) > 8:
                        new_instructions.append(inst)
                        continue

                    param_names = [p.name for p in callee.parameters]
                    args = inst.args

                    # 构建映射：参数名 -> SSA 值（调用者传入）
                    mapper = InlineMapper(inst)
                    for param, arg in zip(param_names, args):
                        mapper.map[param] = arg

                    # 构建参数名到调用者参数名的映射（用于 Load.source 替换）
                    param_name_to_caller_name = {}
                    for p_inst in block.instructions:
                        if type(p_inst).__name__ == "Load":
                            for i, arg in enumerate(args):
                                if p_inst.result == arg:
                                    param_name_to_caller_name[param_names[i]] = p_inst.source
                                    break

                    for i, param in enumerate(param_names):
                        if param not in param_name_to_caller_name and i < len(args):
                            param_name_to_caller_name[param] = param

                    mapper.param_name_to_caller_name = param_name_to_caller_name

                    inline_instructions = []
                    return_value = None
                    value_map = {}

                    for x in callee.blocks[0].instructions:
                        if type(x).__name__ == "Return":
                            return_value = x.value
                            continue

                        # 尝试直接映射（如果是参数 Load，直接返回映射值）
                        mapped = self._try_direct_map(x, mapper)
                        if mapped is not None:
                            if hasattr(x, 'result') and hasattr(mapped, 'id'):
                                inline_results[x.result] = mapped
                            continue

                        # 否则复制指令
                        new_inst = self._copy_instruction(x, value_gen, value_map)
                        self._rewrite_instruction(new_inst, mapper)
                        inline_instructions.append(new_inst)

                    # 处理返回值映射
                    if return_value is not None:
                        if return_value in value_map:
                            resolved_return = value_map[return_value]
                        elif return_value in inline_results:
                            resolved_return = inline_results[return_value]
                        else:
                            resolved_return = mapper.resolve(return_value)

                        if hasattr(inst, "result"):
                            result_map[inst.result] = resolved_return

                    new_instructions.extend(inline_instructions)
                    count += 1

                # 替换所有对 call 结果的引用
                for inst in new_instructions:
                    self._replace_uses(inst, result_map)

                block.instructions = new_instructions

        print(f"  内联函数调用: {count}")
        return module

    def _try_direct_map(self, inst, mapper):
        """尝试直接映射：如果是 Load 参数，直接返回映射值"""
        from compiler.ir.instruction import Load

        if type(inst).__name__ != "Load":
            return None

        if isinstance(inst.source, str) and inst.source in mapper.map:
            return mapper.map[inst.source]

        return None

    def _copy_instruction(self, inst, value_gen, value_map):
        from compiler.ir.instruction import Load, Store, BinaryOp, Return, Const

        inst_type = type(inst)

        if inst_type == Load:
            from compiler.ir.instruction import Load
            new_result = value_gen.next()
            if hasattr(inst, 'result'):
                value_map[inst.result] = new_result
            return Load(result=new_result, source=inst.source)

        elif inst_type == BinaryOp:
            from compiler.ir.instruction import BinaryOp
            new_result = value_gen.next()
            if hasattr(inst, 'result'):
                value_map[inst.result] = new_result
            return BinaryOp(result=new_result, op=inst.op, left=inst.left, right=inst.right)

        elif inst_type == Store:
            from compiler.ir.instruction import Store
            return Store(target=inst.target, value=inst.value)

        elif inst_type == Return:
            from compiler.ir.instruction import Return
            return Return(value=inst.value)

        elif inst_type == Const:
            from compiler.ir.instruction import Const
            new_result = value_gen.next()
            if hasattr(inst, 'result'):
                value_map[inst.result] = new_result
            return Const(result=new_result, value=inst.value)

        else:
            return inst

    def _rewrite_instruction(self, inst, mapper):
        if hasattr(inst, "left"):
            inst.left = mapper.resolve(inst.left)
        if hasattr(inst, "right"):
            inst.right = mapper.resolve(inst.right)
        if hasattr(inst, "value") and inst.value is not None:
            inst.value = mapper.resolve(inst.value)
        if hasattr(inst, "source") and inst.source is not None:
            if isinstance(inst.source, str) and inst.source in mapper.param_name_to_caller_name:
                inst.source = mapper.param_name_to_caller_name[inst.source]

    def _replace_uses(self, inst, result_map):
        if hasattr(inst, "value") and inst.value in result_map:
            inst.value = result_map[inst.value]
        if hasattr(inst, "left") and inst.left in result_map:
            inst.left = result_map[inst.left]
        if hasattr(inst, "right") and inst.right in result_map:
            inst.right = result_map[inst.right]
        if hasattr(inst, "source") and inst.source in result_map:
            inst.source = result_map[inst.source]
