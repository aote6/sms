"""Python AST Generator
IRModule → Python AST → ast.unparse()
"""

from __future__ import annotations

import ast
from compiler.ir import IRModule, IRFunction


class PythonASTCompiler:
    def compile(self, ir: IRModule) -> ast.Module:
        body = []

        # --------------------------------------------------
        # class __init__
        # --------------------------------------------------
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

        class_body = [init_fn]

        # --------------------------------------------------
        # methods
        # --------------------------------------------------
        for fn in ir.functions:
            args = [ast.arg(arg="self")]
            for p in fn.parameters:
                args.append(ast.arg(arg=p.name))

            # 构建 docstring 作为 Expr
            doc_body = []
            if fn.doc:
                doc_body.append(
                    ast.Expr(value=ast.Constant(fn.doc))
                )

            func = ast.FunctionDef(
                name=fn.name,
                args=ast.arguments(
                    posonlyargs=[],
                    args=args,
                    kwonlyargs=[],
                    kw_defaults=[],
                    defaults=[]
                ),
                body=doc_body + [
                    ast.Return(value=ast.Constant(None))
                ],
                decorator_list=[]
            )
            class_body.append(func)

        # --------------------------------------------------
        # class definition
        # --------------------------------------------------
        cls = ast.ClassDef(
            name=ir.name,
            bases=[],
            keywords=[],
            body=class_body,
            decorator_list=[]
        )
        body.append(cls)

        # --------------------------------------------------
        # create() factory function
        # --------------------------------------------------
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

        # --------------------------------------------------
        # module
        # --------------------------------------------------
        module = ast.Module(body=body, type_ignores=[])
        ast.fix_missing_locations(module)
        return module

    def emit(self, ir: IRModule) -> str:
        tree = self.compile(ir)
        return ast.unparse(tree)
