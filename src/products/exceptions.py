class UnsupportedDataTypeError(TypeError):
    """
        Custom exception for unsupported product attribute value types.
    """
    def __init__(self, message="The provided data type is not supported."):
        super().__init__(message)


class CycleInheritanceError(RuntimeError):
    def __init__(self, node=None, message=None):
        self.message = message if message and node else "Cyclic inheritance detected involving node %s" % node
        super().__init__(message)
