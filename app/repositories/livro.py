from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.livro import Livro, Autor
from app.schemas.livro import LivroCreate, LivroUpdate, AutorCreate, AutorUpdate


class LivroRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def criar(self, dados: LivroCreate) -> Livro:
        livro = Livro(**dados.model_dump())
        self._session.add(livro)
        await self._session.flush()
        await self._session.refresh(livro)
        return livro

    async def buscar_por_id(self, livro_id: UUID) -> Optional[Livro]:
        resultado = await self._session.execute(
            select(Livro).where(Livro.id == livro_id)
        )
        return resultado.scalar_one_or_none()

    async def buscar_por_isbn(self, isbn: str) -> Optional[Livro]:
        isbn_limpo = isbn.replace("-", "").replace(" ", "").strip()
        resultado = await self._session.execute(
            select(Livro).where(Livro.isbn == isbn_limpo)
        )
        return resultado.scalar_one_or_none()

    async def listar(
        self,
        pagina: int = 1,
        tamanho: int = 20,
        busca: Optional[str] = None,
        autor_id: Optional[UUID] = None,
        apenas_disponiveis: bool = True,
    ) -> tuple[list[Livro], int]:
        query = select(Livro)

        if apenas_disponiveis:
            query = query.where(Livro.disponivel.is_(True))

        if busca:
            termo = f"%{busca}%"
            query = query.where(
                or_(
                    Livro.titulo.ilike(termo),
                    Livro.isbn.ilike(termo),
                    Livro.sinopse.ilike(termo),
                )
            )

        if autor_id:
            query = query.where(Livro.autor_id == autor_id)

        count_query = select(func.count()).select_from(query.subquery())
        total = await self._session.scalar(count_query) or 0

        offset = (pagina - 1) * tamanho
        query = query.order_by(Livro.titulo.asc()).offset(offset).limit(tamanho)

        resultado = await self._session.execute(query)
        livros = list(resultado.scalars().all())

        return livros, total

    async def atualizar(self, livro: Livro, dados: LivroUpdate) -> Livro:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(livro, campo, valor)
        self._session.add(livro)
        await self._session.flush()
        await self._session.refresh(livro)
        return livro

    async def remover(self, livro: Livro) -> None:
        await self._session.delete(livro)
        await self._session.flush()


class AutorRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def criar(self, dados: AutorCreate) -> Autor:
        autor = Autor(**dados.model_dump())
        self._session.add(autor)
        await self._session.flush()
        await self._session.refresh(autor)
        return autor

    async def buscar_por_id(self, autor_id: UUID) -> Optional[Autor]:
        resultado = await self._session.execute(
            select(Autor).where(Autor.id == autor_id)
        )
        return resultado.scalar_one_or_none()

    async def buscar_por_nome(self, nome: str) -> Optional[Autor]:
        resultado = await self._session.execute(
            select(Autor).where(func.lower(Autor.nome) == nome.lower())
        )
        return resultado.scalar_one_or_none()

    async def listar(self) -> list[Autor]:
        resultado = await self._session.execute(
            select(Autor).order_by(Autor.nome)
        )
        return list(resultado.scalars().all())

    async def atualizar(self, autor: Autor, dados: AutorUpdate) -> Autor:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(autor, campo, valor)
        self._session.add(autor)
        await self._session.flush()
        await self._session.refresh(autor)
        return autor

    async def remover(self, autor: Autor) -> None:
        await self._session.delete(autor)
        await self._session.flush()
