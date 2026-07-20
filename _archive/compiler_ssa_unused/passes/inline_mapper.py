"""InlineMapper - 内联参数映射"""


class InlineMapper:
    def __init__(self, call_inst):
        self.map = {}
        self.param_name_to_caller_name = {}
        self.call_result = getattr(call_inst, 'result', None)

    def set_params(self, param_names, args):
        for param, arg in zip(param_names, args):
            self.map[param] = arg

    def resolve(self, value):
        if value is None:
            return None
        if isinstance(value, str):
            return self.map.get(value, value)
        return value
