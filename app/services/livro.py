import math
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.livro import LivroRepository, AutorRepository
from app.schemas.livro import (
    LivroCreate,
    LivroUpdate,
    LivroResponse,
    AutorCreate,
    AutorUpdate,
    AutorResponse,
    RespostaPaginada,
)
from app.core.exceptions import ConflitoError, NaoEncontradoError, RegraDeNegocioError


class LivroService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = LivroRepository(session)
        self._autor_repo = AutorRepository(session)

    async def cadastrar_livro(self, dados: LivroCreate) -> LivroResponse:
        existente = await self._repo.buscar_por_isbn(dados.isbn)
        if existente:
            raise ConflitoError(f"ISBN '{dados.isbn}' já está cadastrado.")

        if dados.autor_id:
            autor = await self._autor_repo.buscar_por_id(dados.autor_id)
            if not autor:
                raise NaoEncontradoError(f"Autor '{dados.autor_id}' não encontrado.")

        livro = await self._repo.criar(dados)
        return LivroResponse.model_validate(livro)

    async def consultar_livro(self, livro_id: UUID) -> LivroResponse:
        livro = await self._repo.buscar_por_id(livro_id)
        if not livro:
            raise NaoEncontradoError(f"Livro '{livro_id}' não encontrado.")
        return LivroResponse.model_validate(livro)

    async def listar_livros(
        self,
        pagina: int = 1,
        tamanho: int = 20,
        busca: Optional[str] = None,
        autor_id: Optional[UUID] = None,
        apenas_disponiveis: bool = True,
    ) -> RespostaPaginada:
        livros, total = await self._repo.listar(
            pagina=pagina,
            tamanho=tamanho,
            busca=busca,
            autor_id=autor_id,
            apenas_disponiveis=apenas_disponiveis,
        )
        return RespostaPaginada(
            total=total,
            pagina=pagina,
            tamanho=tamanho,
            paginas=math.ceil(total / tamanho) if total else 0,
            itens=[LivroResponse.model_validate(l) for l in livros],
        )

    async def atualizar_livro(self, livro_id: UUID, dados: LivroUpdate) -> LivroResponse:
        livro = await self._repo.buscar_por_id(livro_id)
        if not livro:
            raise NaoEncontradoError(f"Livro '{livro_id}' não encontrado.")

        if dados.autor_id:
            autor = await self._autor_repo.buscar_por_id(dados.autor_id)
            if not autor:
                raise NaoEncontradoError(f"Autor '{dados.autor_id}' não encontrado.")

        livro = await self._repo.atualizar(livro, dados)
        return LivroResponse.model_validate(livro)

    async def excluir_livro(self, livro_id: UUID) -> None:
        livro = await self._repo.buscar_por_id(livro_id)
        if not livro:
            raise NaoEncontradoError(f"Livro '{livro_id}' não encontrado.")
        await self._repo.remover(livro)


class AutorService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = AutorRepository(session)

    async def cadastrar_autor(self, dados: AutorCreate) -> AutorResponse:
        existente = await self._repo.buscar_por_nome(dados.nome)
        if existente:
            raise ConflitoError(f"Autor '{dados.nome}' já está cadastrado.")
        autor = await self._repo.criar(dados)
        return AutorResponse.model_validate(autor)

    async def listar_autores(self) -> list[AutorResponse]:
        autores = await self._repo.listar()
        return [AutorResponse.model_validate(a) for a in autores]

    async def consultar_autor(self, autor_id: UUID) -> AutorResponse:
        autor = await self._repo.buscar_por_id(autor_id)
        if not autor:
            raise NaoEncontradoError(f"Autor '{autor_id}' não encontrado.")
        return AutorResponse.model_validate(autor)

    async def atualizar_autor(self, autor_id: UUID, dados: AutorUpdate) -> AutorResponse:
        autor = await self._repo.buscar_por_id(autor_id)
        if not autor:
            raise NaoEncontradoError(f"Autor '{autor_id}' não encontrado.")

        if dados.nome:
            existente = await self._repo.buscar_por_nome(dados.nome)
            if existente and existente.id != autor_id:
                raise ConflitoError(f"Autor '{dados.nome}' já existe.")

        autor = await self._repo.atualizar(autor, dados)
        return AutorResponse.model_validate(autor)

    async def excluir_autor(self, autor_id: UUID) -> None:
        autor = await self._repo.buscar_por_id(autor_id)
        if not autor:
            raise NaoEncontradoError(f"Autor '{autor_id}' não encontrado.")
        await self._repo.remover(autor)
