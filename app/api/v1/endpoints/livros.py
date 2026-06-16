from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.livro import (
    LivroCreate,
    LivroUpdate,
    LivroResponse,
    RespostaPaginada,
)
from app.services.livro import LivroService
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/livros", tags=["Livros"])


def get_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LivroService:
    return LivroService(db)


@router.post(
    "/",
    response_model=LivroResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar livro",
)
async def cadastrar_livro(
    dados: LivroCreate,
    service: Annotated[LivroService, Depends(get_service)],
) -> LivroResponse:
    """Cadastra um novo livro no acervo."""
    return await service.cadastrar_livro(dados)


@router.get(
    "/",
    response_model=RespostaPaginada,
    summary="Listar livros",
)
async def listar_livros(
    service: Annotated[LivroService, Depends(get_service)],
    pagina: int = Query(default=1, ge=1, description="Número da página"),
    tamanho: int = Query(
        default=settings.PAGINA_PADRAO,
        ge=1,
        le=settings.PAGINA_MAXIMA,
        description="Itens por página",
    ),
    busca: Optional[str] = Query(
        default=None,
        min_length=2,
        description="Busca por título, ISBN ou sinopse",
    ),
    autor_id: Optional[UUID] = Query(
        default=None, description="Filtrar por autor"
    ),
    apenas_disponiveis: bool = Query(
        default=True, description="Retornar apenas livros disponíveis"
    ),
) -> RespostaPaginada:
    """Lista livros com suporte a busca, filtros e paginação."""
    return await service.listar_livros(
        pagina=pagina,
        tamanho=tamanho,
        busca=busca,
        autor_id=autor_id,
        apenas_disponiveis=apenas_disponiveis,
    )


@router.get(
    "/{livro_id}",
    response_model=LivroResponse,
    summary="Consultar livro",
)
async def consultar_livro(
    livro_id: UUID,
    service: Annotated[LivroService, Depends(get_service)],
) -> LivroResponse:
    """Retorna um livro pelo ID."""
    return await service.consultar_livro(livro_id)


@router.patch(
    "/{livro_id}",
    response_model=LivroResponse,
    summary="Atualizar livro",
)
async def atualizar_livro(
    livro_id: UUID,
    dados: LivroUpdate,
    service: Annotated[LivroService, Depends(get_service)],
) -> LivroResponse:
    """Atualiza parcialmente um livro existente."""
    return await service.atualizar_livro(livro_id, dados)


@router.delete(
    "/{livro_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir livro",
)
async def excluir_livro(
    livro_id: UUID,
    service: Annotated[LivroService, Depends(get_service)],
) -> None:
    """Remove permanentemente um livro do acervo."""
    await service.excluir_livro(livro_id)
