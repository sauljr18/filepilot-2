"""Erro de contrato do FilePilot (SPEC 6)."""


class FilePilotError(Exception):
    """Falha de contrato dos servicos, com codigo, mensagem e campos invalidos."""

    def __init__(
        self,
        code: str,
        message: str,
        fields: dict[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.fields = fields
