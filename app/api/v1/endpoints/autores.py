from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.livro import (
    AutorCreate,
    AutorUpdate,
    AutorResponse,
)
from app.services.livro import AutorService

router = APIRouter(prefix="/autores", tags=["Autores"])


def get_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AutorService:
    return AutorService(db)


@router.post(
    "/",
    response_model=AutorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar autor",
)
async def cadastrar_autor(
    dados: AutorCreate,
    service: Annotated[AutorService, Depends(get_service)],
) -> AutorResponse:
    return await service.cadastrar_autor(dados)


@router.get(
    "/",
    response_model=list[AutorResponse],
    summary="Listar autores",
)
async def listar_autores(
    service: Annotated[AutorService, Depends(get_service)],
) -> list[AutorResponse]:
    return await service.listar_autores()


@router.get(
    "/{autor_id}",
    response_model=AutorResponse,
    summary="Consultar autor",
)
async def consultar_autor(
    autor_id: UUID,
    service: Annotated[AutorService, Depends(get_service)],
) -> AutorResponse:
    return await service.consultar_autor(autor_id)


@router.patch(
    "/{autor_id}",
    response_model=AutorResponse,
    summary="Atualizar autor",
)
async def atualizar_autor(
    autor_id: UUID,
    dados: AutorUpdate,
    service: Annotated[AutorService, Depends(get_service)],
) -> AutorResponse:
    return await service.atualizar_autor(autor_id, dados)


@router.delete(
    "/{autor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir autor",
)
async def excluir_autor(
    autor_id: UUID,
    service: Annotated[AutorService, Depends(get_service)],
) -> None:
    await service.excluir_autor(autor_id)
