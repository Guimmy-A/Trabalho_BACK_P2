from fastapi import APIRouter

from app.api.v1.endpoints import livros, autores

api_router = APIRouter()
api_router.include_router(livros.router)
api_router.include_router(autores.router)
