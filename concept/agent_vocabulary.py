"""
Agent 能力标准词汇表（含行为模板）
"""
from concept import ConceptRegistry, Concept

def init_agent_concepts(reg: ConceptRegistry):
    """注册 Agent 领域标准能力词汇"""
    concepts = [
        Concept(
            concept_id="cap.agent.tool.code",
            name="ToolCode",
            aliases=['code_execution', 'run_code', '代码执行', 'tool_code', 'toolcode'],
            description="执行代码并返回结果",
            inputs=['code: str', 'language: str'],
            outputs=['output: str'],
            metadata={'behavior': 'code_executor', 'template': 'exec', 'sandbox': True, 'timeout': 30},
        ),
        Concept(
            concept_id="cap.agent.tool.file",
            name="ToolFile",
            aliases=['file_operation', 'read_file', 'write_file', '文件操作', 'tool_file', 'toolfile'],
            description="读写文件系统",
            inputs=['path: str', 'operation: str'],
            outputs=['data: str'],
            metadata={'behavior': 'file_operator', 'template': 'file_io'},
        ),
        Concept(
            concept_id="cap.agent.memory.short_term",
            name="ShortTermMemory",
            aliases=['short_memory', 'working_memory', '短期记忆', 'short_term_memory', 'shorttermmemory'],
            description="短期记忆",
            inputs=['key: str', 'value: Any'],
            outputs=['data: Any'],
            metadata={'behavior': 'dict_store', 'template': 'memory', 'max_size': 100},
        ),
        Concept(
            concept_id="cap.agent.memory.long_term",
            name="LongTermMemory",
            aliases=['long_memory', 'persistent_memory', '长期记忆', 'long_term_memory', 'longtermmemory'],
            description="长期记忆",
            inputs=['data: Any'],
            outputs=['stored_id: str'],
            metadata={'behavior': 'file_store', 'template': 'persistent_memory'},
        ),
        Concept(
            concept_id="cap.agent.planner.sequential",
            name="SequentialPlanner",
            aliases=['sequential', 'step_by_step', '顺序规划', 'sequential_planner', 'sequentialplanner'],
            description="任务分解",
            inputs=['task: str'],
            outputs=['steps: list'],
            metadata={'behavior': 'llm_planner', 'template': 'sequential_plan', 'prompt': '将以下任务分解为有序步骤:'},
        ),
        Concept(
            concept_id="cap.agent.planner.react",
            name="ReActPlanner",
            aliases=['react', 'reasoning_action', '思考行动', 'react_planner', 'reactplanner'],
            description="Think-Act-Observe",
            inputs=['observation: str'],
            outputs=['action: str'],
            metadata={'behavior': 'llm_react', 'template': 'react_loop', 'max_iterations': 5},
        ),
        Concept(
            concept_id="cap.agent.executor.tool_invoker",
            name="ToolInvoker",
            aliases=['invoke_tool', 'call_tool', '工具调用', 'tool_invoker', 'toolinvoker'],
            description="动态调用工具",
            inputs=['tool_name: str', 'parameters: dict'],
            outputs=['result: Any'],
            metadata={'behavior': 'dispatcher', 'template': 'tool_dispatch'},
        ),
        Concept(
            concept_id="cap.agent.protocol.request",
            name="RequestProtocol",
            aliases=['request', 'ask', '请求', 'request_protocol', 'requestprotocol'],
            description="请求-响应通信",
            inputs=['message: str'],
            outputs=['response: str'],
            metadata={'behavior': 'message_pass', 'template': 'request_response'},
        ),
        Concept(
            concept_id="cap.agent.protocol.debate",
            name="DebateProtocol",
            aliases=['debate', 'discuss', '辩论', 'debate_protocol', 'debateprotocol'],
            description="多 Agent 辩论",
            inputs=['proposal: str'],
            outputs=['consensus: str'],
            metadata={'behavior': 'llm_debate', 'template': 'debate', 'rounds': 3},
        ),
    ]
    for c in concepts:
        reg.register(c)
    return reg
