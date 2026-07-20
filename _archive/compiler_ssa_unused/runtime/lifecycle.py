"""Lifecycle - 生命周期状态"""


class Lifecycle:
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    STOPPED = "stopped"

    @classmethod
    def all(cls):
        return [cls.CREATED, cls.STARTING, cls.RUNNING, cls.STOPPED]
