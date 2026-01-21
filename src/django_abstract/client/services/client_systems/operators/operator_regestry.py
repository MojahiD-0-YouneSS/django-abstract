OPERATOR_REGISTRY = {}
SYSTEM_REGISTRY = {}

def register_operator():
    def decorator(cls):
        OPERATOR_REGISTRY[cls.domain]=cls
        return cls
    return decorator

def register_service():
    def decorator(cls):
        SYSTEM_REGISTRY[cls.domain]=cls
        return cls
    return decorator

