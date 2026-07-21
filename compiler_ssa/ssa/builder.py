"""SSA Builder - Phi 插入 + 变量重命名"""

from compiler_ssa.ssa.phi import PhiInserter
from compiler_ssa.ssa.rename import SSARename
from compiler_ssa.ssa_core import Phi


class SSABuilder:
    def __init__(self):
        self.phi_inserter = PhiInserter()
        self.rename = SSARename()

    def build(self, fn):
        print(f"\n📦 构建 SSA: {fn.name}")

        # 1. Phi 插入
        self.phi_inserter.insert(fn)
        print(f"   ✅ Phi 节点插入完成")

        # 2. 打印 Phi 节点
        self.print_phis(fn)

        # 3. Rename
        self.rename.run(fn)
        print(f"   ✅ Rename 完成")

        # 4. 打印 SSA
        self.print_ssa(fn)

        return fn

    def print_phis(self, fn):
        print()
        print("=" * 50)
        print("Phi 节点")
        print("=" * 50)
        for block in fn.blocks:
            phis = [inst for inst in block.instructions if isinstance(inst, Phi)]
            if phis:
                print(f"  {block.name}:")
                for phi in phis:
                    print(f"    {phi}")
        print("=" * 50)

    def print_ssa(self, fn):
        print()
        print("=" * 50)
        print("SSA")
        print("=" * 50)
        for block in fn.blocks:
            print(f"\n  {block.name}:")
            for inst in block.instructions:
                print(f"    {inst}")
        print("=" * 50)
