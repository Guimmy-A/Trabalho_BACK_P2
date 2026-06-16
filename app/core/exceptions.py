class AppError(Exception):
    """Exceção base da aplicação."""

    def __init__(self, mensagem: str, status_code: int = 500) -> None:
        self.mensagem = mensagem
        self.status_code = status_code
        super().__init__(mensagem)


class NaoEncontradoError(AppError):
    def __init__(self, mensagem: str = "Recurso não encontrado.") -> None:
        super().__init__(mensagem, status_code=404)


class ConflitoError(AppError):
    def __init__(self, mensagem: str = "Conflito de dados.") -> None:
        super().__init__(mensagem, status_code=409)


class RegraDeNegocioError(AppError):
    def __init__(self, mensagem: str = "Operação não permitida.") -> None:
        super().__init__(mensagem, status_code=422)
