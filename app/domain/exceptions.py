"""Domain-level exceptions for the hexagonal architecture application."""


class EmailAlreadyRegisteredError(Exception):
    """Raised when a user attempts to register with an already existing email."""

    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Email already registered: {email}")
