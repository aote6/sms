class Calculator:

    def __init__(self):
        self.version = '1.0.0'

    def add(self, a, b):
        v0 = a
        v1 = b
        v2 = v0 + v1
        return v2

def create():
    return Calculator()