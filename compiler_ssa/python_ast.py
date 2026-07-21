"""Python AST Generator
IRModule → Python AST → ast.unparse()
"""

from __future__ import annotations

import ast
from compiler_ssa.ir import IRModule, IRFunction, IRBlock
from compiler_ssa.ir.instruction import Load, Store, Return, BinaryOp, Call, Const
from compiler_ssa.instructions import Branch, Jump, Compare
from compiler_ssa.ssa_core import SSAValue


class PythonASTCompiler:
    def __init__(self):
        self._value_names = {}

    def _value_to_python(self, value: str) -> str:
        if value is None:
            return None
        if value.startswith("%"):
            return f"v{value[1:]}"
        return value

    def compile(self, ir: IRModule) -> ast.Module:
        body = []
        class_body = []

        init_body = [
            ast.Assign(
                targets=[
                    ast.Attribute(
                        value=ast.Name("self", ast.Load()),
                        attr="version",
                        ctx=ast.Store()
                    )
                ],
                value=ast.Constant(ir.version)
            )
        ]
        init_fn = ast.FunctionDef(
            name="__init__",
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self")],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]
            ),
            body=init_body,
            decorator_list=[]
        )
        class_body.append(init_fn)

        for fn in ir.functions:
            method = self._compile_function_to_method(fn)
            class_body.append(method)

        cls = ast.ClassDef(
            name=ir.name,
            bases=[],
            keywords=[],
            body=class_body,
            decorator_list=[]
        )
        body.append(cls)

        create_fn = ast.FunctionDef(
            name="create",
            args=ast.arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]
            ),
            body=[
                ast.Return(
                    value=ast.Call(
                        func=ast.Name(id=ir.name, ctx=ast.Load()),
                        args=[],
                        keywords=[]
                    )
                )
            ],
            decorator_list=[]
        )
        body.append(create_fn)

        module = ast.Module(body=body, type_ignores=[])
        ast.fix_missing_locations(module)
        return module

    def _compile_function_to_method(self, fn: IRFunction) -> ast.FunctionDef:
        args = [ast.arg(arg="self")]
        for p in fn.parameters:
            args.append(ast.arg(arg=p.name))

        body = []
        if fn.blocks:
            entry = fn.blocks[0]
            for inst in entry.instructions:
                stmts = self._compile_instruction(inst)
                body.extend(stmts)

        if not body or not isinstance(body[-1], ast.Return):
            body.append(ast.Return(value=ast.Constant(None)))

        return ast.FunctionDef(
            name=fn.name,
            args=ast.arguments(
                posonlyargs=[],
                args=args,
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]
            ),
            body=body,
            decorator_list=[],
        )

    def _compile_instruction(self, inst):
        if isinstance(inst, Load):
            target_name = self._value_to_python(inst.result)
            source_name = self._value_to_python(inst.source)
            return [ast.Assign(
                targets=[ast.Name(id=target_name, ctx=ast.Store())],
                value=ast.Name(id=source_name, ctx=ast.Load())
            )]
        elif isinstance(inst, BinaryOp):
            left_name = self._value_to_python(inst.left)
            right_name = self._value_to_python(inst.right)
            left = ast.Name(id=left_name, ctx=ast.Load())
            right = ast.Name(id=right_name, ctx=ast.Load())

            if inst.op == "+":
                expr = ast.BinOp(left=left, op=ast.Add(), right=right)
            elif inst.op == "-":
                expr = ast.BinOp(left=left, op=ast.Sub(), right=right)
            elif inst.op == "*":
                expr = ast.BinOp(left=left, op=ast.Mult(), right=right)
            elif inst.op == "/":
                expr = ast.BinOp(left=left, op=ast.Div(), right=right)
            else:
                expr = ast.Constant(None)

            target_name = self._value_to_python(inst.result)
            return [ast.Assign(
                targets=[ast.Name(id=target_name, ctx=ast.Store())],
                value=expr
            )]
        elif isinstance(inst, Return):
            if inst.value:
                val_name = self._value_to_python(inst.value)
                return [ast.Return(value=ast.Name(id=val_name, ctx=ast.Load()))]
            else:
                return [ast.Return(value=ast.Constant(None))]
        elif isinstance(inst, Const):
            target_name = self._value_to_python(inst.result)
            return [ast.Assign(
                targets=[ast.Name(id=target_name, ctx=ast.Store())],
                value=ast.Constant(inst.value)
            )]
        elif isinstance(inst, Call):
            args = [ast.Name(id=a, ctx=ast.Load()) for a in inst.args]
            call_expr = ast.Call(
                func=ast.Name(id=inst.fn_name, ctx=ast.Load()),
                args=args,
                keywords=[]
            )
            target_name = self._value_to_python(inst.result)
            return [ast.Assign(
                targets=[ast.Name(id=target_name, ctx=ast.Store())],
                value=call_expr
            )]
        else:
            return []

    def emit(self, ir: IRModule) -> str:
        tree = self.compile(ir)
        return ast.unparse(tree)
