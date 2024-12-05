class UnsupportedDataTypeError(TypeError):
    """Custom exception for unsupported product attribute value types."""
    def __init__(self, message="The provided data type is not supported."):
        super().__init__(message)
