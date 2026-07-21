"""
Agent 能力标准词汇表
SMS Concept Registry 初始化数据
"""

from concept import ConceptRegistry, Concept

def init_agent_concepts(reg: ConceptRegistry):
    """向 ConceptRegistry 注册 Agent 领域的标准能力词汇"""

    concepts = [
        # Tool 工具
        Concept("cap.agent.tool", "Tool", "Agent 可调用的外部工具",
                ["tool", "agent_tool", "function_call", "tool_call", "工具"],
                ["parameters"], ["result"]),
        Concept("cap.agent.tool.search", "ToolSearch", "搜索工具",
                ["search", "web_search", "检索", "搜索"],
                ["query"], ["results"], parent="cap.agent.tool"),
        Concept("cap.agent.tool.file", "ToolFile", "文件操作工具",
                ["file_operation", "read_file", "write_file", "文件操作"],
                ["path", "operation"], ["data"], parent="cap.agent.tool"),
        Concept("cap.agent.tool.code", "ToolCode", "代码执行工具",
                ["code_execution", "run_code", "代码执行"],
                ["code", "language"], ["output"], parent="cap.agent.tool"),

        # Memory 记忆
        Concept("cap.agent.memory", "Memory", "Agent 的记忆存储能力",
                ["memory", "agent_memory", "context", "state", "记忆"],
                ["key", "value"], ["data"]),
        Concept("cap.agent.memory.short_term", "ShortTermMemory", "短期记忆",
                ["short_memory", "working_memory", "短期记忆"],
                ["context"], ["memory_state"], parent="cap.agent.memory"),
        Concept("cap.agent.memory.long_term", "LongTermMemory", "长期记忆",
                ["long_memory", "persistent_memory", "长期记忆"],
                ["data"], ["stored_data"], parent="cap.agent.memory"),

        # Planner 规划
        Concept("cap.agent.planner", "Planner", "Agent 的任务规划与推理",
                ["planner", "planning", "reasoning", "规划"],
                ["goal", "context"], ["plan"]),
        Concept("cap.agent.planner.sequential", "SequentialPlanner", "顺序规划器",
                ["sequential", "step_by_step", "顺序规划"],
                ["task"], ["steps"], parent="cap.agent.planner"),
        Concept("cap.agent.planner.react", "ReActPlanner", "ReAct 模式",
                ["react", "reasoning_action", "思考行动"],
                ["observation"], ["action"], parent="cap.agent.planner"),

        # Executor 执行
        Concept("cap.agent.executor", "Executor", "Agent 的行动执行",
                ["executor", "execute", "action", "执行"],
                ["action_plan"], ["result"]),
        Concept("cap.agent.executor.tool_invoker", "ToolInvoker", "工具调用执行器",
                ["invoke_tool", "call_tool", "工具调用"],
                ["tool_name", "parameters"], ["tool_result"], parent="cap.agent.executor"),

        # Protocol 通信
        Concept("cap.agent.protocol", "AgentProtocol", "Agent 间通信协议",
                ["protocol", "communication", "message", "通信协议", "协议"],
                ["message"], ["response"]),
        Concept("cap.agent.protocol.request", "RequestProtocol", "请求-响应模式",
                ["request", "ask", "请求"],
                ["request_data"], ["response_data"], parent="cap.agent.protocol"),
        Concept("cap.agent.protocol.debate", "DebateProtocol", "多 Agent 辩论协议",
                ["debate", "discuss", "辩论"],
                ["proposal"], ["consensus"], parent="cap.agent.protocol"),
    ]

    for c in concepts:
        reg.register(c)

    return reg
