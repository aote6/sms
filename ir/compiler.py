from module import Module
from .ir import IRModule, IRFunction


class IRCompiler:
    def __init__(self, concept_registry=None):
        self.concepts = concept_registry

    def compile(self, module: Module) -> IRModule:
        ir = IRModule(
            name=module.name,
            version=module.version,
            runtime=module.contract.runtime if module.contract else "unknown",
            imports=self._gen_imports(module),
            metadata={
                "quality_state": module.quality_state,
                "package_type": module.package_type,
                "origin": module.origin,
                "capabilities": [c.name for c in module.capabilities]
            }
        )

        for cap in module.capabilities:
            fn = self._compile_capability(cap, module)
            ir.functions.append(fn)

        return ir

    def _compile_capability(self, cap, module) -> IRFunction:
        concept = None
        if self.concepts:
            concept = self.concepts.find(cap.name)

        body = []
        doc = cap.description

        if concept:
            doc = concept.description
            body.append(f"# 概念: {concept.concept_id}")
            behavior = concept.metadata.get("behavior", "default")
            
            # 根据行为模板生成真实代码
            if behavior == "code_executor":
                body.extend(self._gen_code_executor(cap))
            elif behavior == "dict_store":
                body.extend(self._gen_dict_store(cap))
            elif behavior == "file_operator":
                body.extend(self._gen_file_operator(cap))
            elif behavior == "file_store":
                body.extend(self._gen_file_store(cap))
            elif behavior == "llm_planner":
                body.extend(self._gen_llm_planner(concept, cap))
            elif behavior == "llm_react":
                body.extend(self._gen_llm_react(concept, cap))
            elif behavior == "dispatcher":
                body.extend(self._gen_dispatcher(cap))
            elif behavior == "message_pass":
                body.extend(self._gen_message_pass(cap))
            elif behavior == "llm_debate":
                body.extend(self._gen_llm_debate(concept, cap))
            else:
                body.extend(self._gen_default(cap))
        else:
            body.append(f"# 能力: {cap.name} (未注册)")
            body.extend(self._gen_default(cap))

        return IRFunction(
            name=cap.name,
            inputs=[cap.input_type],
            output=cap.output_type,
            doc=doc,
            body=body
        )

    def _gen_code_executor(self, cap) -> list:
        return [
            "import subprocess, tempfile, os",
            f"print(f\"[{{self.__class__.__name__}}] 执行代码...\")",
            "try:",
            "    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:",
            "        f.write(code)",
            "        tmpname = f.name",
            "    result = subprocess.run(['python3', tmpname], capture_output=True, text=True, timeout=30)",
            "    os.unlink(tmpname)",
            "    output = result.stdout or result.stderr",
            "    return {'status': 'ok', 'output': output}",
            "except Exception as e:",
            "    return {'status': 'error', 'error': str(e)}",
        ]

    def _gen_dict_store(self, cap) -> list:
        return [
            "if not hasattr(self, '_memory'):",
            "    self._memory = {}",
            f"print(f\"[{{self.__class__.__name__}}] 记忆操作: key={{key}}\")",
            "if value is not None:",
            "    self._memory[key] = value",
            "    return {'status': 'stored', 'key': key}",
            "return {'status': 'retrieved', 'key': key, 'data': self._memory.get(key)}",
        ]

    def _gen_file_operator(self, cap) -> list:
        return [
            "import os",
            f"print(f\"[{{self.__class__.__name__}}] 文件操作: {{operation}} {{path}}\")",
            "if operation == 'read':",
            "    if os.path.exists(path):",
            "        with open(path) as f:",
            "            return {'status': 'ok', 'data': f.read()}",
            "    return {'status': 'error', 'error': 'file not found'}",
            "elif operation == 'write':",
            "    with open(path, 'w') as f:",
            "        f.write(data)",
            "    return {'status': 'ok'}",
            "return {'status': 'error', 'error': f'unknown operation: {operation}'}",
        ]

    def _gen_file_store(self, cap) -> list:
        return [
            "import json, os, time",
            f"print(f\"[{{self.__class__.__name__}}] 持久化存储...\")",
            "store_dir = '.sms_memory'",
            "os.makedirs(store_dir, exist_ok=True)",
            "stored_id = str(int(time.time() * 1000))",
            "with open(os.path.join(store_dir, f'{stored_id}.json'), 'w') as f:",
            "    json.dump(data, f, ensure_ascii=False)",
            "return {'status': 'stored', 'id': stored_id}",
        ]

    def _gen_llm_planner(self, concept, cap) -> list:
        prompt = concept.metadata.get("prompt", "将以下任务分解为有序步骤:")
        return [
            f"print(f\"[{{self.__class__.__name__}}] 规划任务: {{task}}\")",
            f"# LLM 调用接口（可替换为真实 API）",
            f"prompt = \"{prompt}\"",
            "# TODO: 替换为真实 LLM 调用",
            "# response = llm.chat(prompt + '\\n' + task)",
            "steps = [",
            "    f\"分析: {task}\",",
            "    f\"设计: {task}的解决方案\",",
            "    f\"实现: 编写代码\",",
            "    f\"测试: 验证结果\"",
            "]",
            "print(f\"  规划步骤: {len(steps)} 步\")",
            "return {'status': 'ok', 'steps': steps, 'prompt_used': prompt}",
        ]

    def _gen_llm_react(self, concept, cap) -> list:
        max_iter = concept.metadata.get("max_iterations", 5)
        return [
            f"print(f\"[{{self.__class__.__name__}}] ReAct 循环 (最多 {max_iter} 轮)\")",
            "# TODO: 替换为真实 LLM ReAct 循环",
            "action = f\"基于观察 '{observation}'，采取行动\"",
            "return {'status': 'ok', 'action': action, 'observation': observation}",
        ]

    def _gen_dispatcher(self, cap) -> list:
        return [
            f"print(f\"[{{self.__class__.__name__}}] 工具调度: {{tool_name}}\")",
            "# 动态调用模块内其他方法",
            "if hasattr(self, tool_name):",
            "    tool_method = getattr(self, tool_name)",
            "    return tool_method(**parameters) if parameters else tool_method('')",
            "return {'status': 'error', 'error': f'工具未找到: {tool_name}'}",
        ]

    def _gen_message_pass(self, cap) -> list:
        return [
            f"print(f\"[{{self.__class__.__name__}}] 收到消息: {{message}}\")",
            "response = f\"已处理: {message}\"",
            "return {'status': 'ok', 'response': response, 'original': message}",
        ]

    def _gen_llm_debate(self, concept, cap) -> list:
        rounds = concept.metadata.get("rounds", 3)
        return [
            f"print(f\"[{{self.__class__.__name__}}] 辩论开始 ({rounds} 轮)\")",
            "# TODO: 替换为真实多 Agent 辩论",
            f"consensus = f\"经过{rounds}轮辩论，关于'{{proposal}}'达成共识\"",
            "return {'status': 'ok', 'consensus': consensus, 'rounds': " + str(rounds) + "}",
        ]

    def _gen_default(self, cap) -> list:
        cap_name = cap.name
        return [
            f"print(f\"[{{self.__class__.__name__}}] {cap_name}: 已调用\")",
            f"return {{'status': 'ok', 'capability': '{cap_name}'}}",
        ]

    def _gen_imports(self, module: Module) -> list[str]:
        imports = ["from typing import Any"]
        return imports

    def compile_all(self, modules: list[Module]) -> list[IRModule]:
        return [self.compile(m) for m in modules]
