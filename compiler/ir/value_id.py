class ValueId:
    """SSA 风格的值 ID 生成器"""
    
    def __init__(self):
        self._id = 0
    
    def next(self):
        name = f"%{self._id}"
        self._id += 1
        return name
    
    def reset(self):
        self._id = 0
