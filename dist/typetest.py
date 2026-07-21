# 由 SMS 生成
# 模块: TypeTest v1.0.0
# 后端: python
# 能力: []

from typing import Any, get_type_hints
import inspect

class TypeTest:
    """TypeTest 实现"""

    def __init__(self):
        self.version = "1.0.0"
        self._initialized = True

    def typemod_do_work(self, a: str,b:int) -> dict:
        """干活"""
        # 能力: do_work (未注册)
        print(f"[{self.__class__.__name__}] do_work: 已调用")
        return {'status': 'ok', 'capability': 'do_work'}

    def validate(self, ) -> bool:
        """运行时自检：参数个数 + 类型检查"""
        print("🔍 运行时自检...")
        errors = []
        sig = inspect.signature(self.typemod_do_work)
        params = [p for p in sig.parameters if p != 'self']
        if len(params) != 2:
            errors.append(f"❌ typemod_do_work: 期望2个参数，实际{len(params)}个 → 必崩")
        else:
            print(f"  ✅ typemod_do_work: {len(params)}个参数 OK")
            hints = get_type_hints(self.typemod_do_work)
            if 'a' in hints:
                actual_type = hints['a'].__name__ if hasattr(hints['a'], '__name__') else str(hints['a'])
                expected = 'str'
                if actual_type.lower() != expected.lower() and expected.lower() != 'any':
                    errors.append(f"⚠️ typemod_do_work.a: 类型标注是{actual_type}，期望str")
                else:
                    print(f"    ✅ a: {actual_type} (期望str)")
            if 'b' in hints:
                actual_type = hints['b'].__name__ if hasattr(hints['b'], '__name__') else str(hints['b'])
                expected = 'int'
                if actual_type.lower() != expected.lower() and expected.lower() != 'any':
                    errors.append(f"⚠️ typemod_do_work.b: 类型标注是{actual_type}，期望int")
                else:
                    print(f"    ✅ b: {actual_type} (期望int)")
        if errors:
            print('\n'.join(errors))
            return False
        print('  ✅ 全部参数验证通过')
        return True

    def main(self, ) -> dict:
        """产品入口: TypeTest"""
        print("产品: TypeTest")
        print("包含模块: ['TypeMod']")
        
        if not self.validate():
            print("\n❌ 自检失败，中止运行")
            return {"status": "validation_failed"}
        
        results = {}
        results["typemod_do_work"] = self.typemod_do_work("test_key", "test_value")
        print(f"  {results['typemod_do_work']}")
        
        print(f"\n所有能力已执行: {len(results)} 个")
        return results


def create():
    """工厂方法"""
    return TypeTest()

if __name__ == "__main__":
    instance = create()
    print(f"✅ TypeTest v{instance.version} 已加载")
    print("\n执行 main 入口...")
    result = instance.main()
    print(f"结果: {result}")
