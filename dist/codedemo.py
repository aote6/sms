# 由 SMS 生成
# 模块: CodeDemo v1.0.0
# 后端: python
# 能力: []

from typing import Any

class CodeDemo:
    """CodeDemo 实现"""

    def __init__(self):
        self.version = "1.0.0"
        self._initialized = True

    def coderunner_ToolCode(self, code: str,language:str) -> str:
        """执行代码并返回结果"""
        # 概念: cap.agent.tool.code
        import subprocess, tempfile, os
        print(f"[{self.__class__.__name__}] 执行代码...")
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                tmpname = f.name
            result = subprocess.run(['python3', tmpname], capture_output=True, text=True, timeout=30)
            os.unlink(tmpname)
            output = result.stdout or result.stderr
            return {'status': 'ok', 'output': output}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def main(self, ) -> dict:
        """产品入口: CodeDemo"""
        print("产品: CodeDemo")
        print("包含模块: ['CodeRunner']")
        
        results = {}
        # 调用 coderunner_ToolCode("test_key", "test_value")
        results["coderunner_ToolCode"] = self.coderunner_ToolCode("""print("Hello from SMS!")\nprint(1 + 1)\nprint([i**2 for i in range(5)])""", "python")
        print(f"  {results['coderunner_ToolCode']}")
        
        print(f"\n所有能力已执行: {len(results)} 个")
        return results


def create():
    """工厂方法"""
    return CodeDemo()

if __name__ == "__main__":
    instance = create()
    print(f"✅ CodeDemo v{instance.version} 已加载")
    print("\n执行 main 入口...")
    result = instance.main()
    print(f"结果: {result}")
