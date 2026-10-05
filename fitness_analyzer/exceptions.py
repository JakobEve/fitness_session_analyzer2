class InvalidIdentifierError(ValueError):
    """Raised when an identifier has an invalid format."""

    def __init__(self, field, reason):
        super().__init__(f"{field}: {reason}")
        self.field = field
        self.reason = reason


class InvalidRecordError(ValueError):
    """Raised when a CSV record cannot be accepted."""

    def __init__(self, field, reason):
        super().__init__(f"{field}: {reason}")
        self.field = field
        self.reason = reason
