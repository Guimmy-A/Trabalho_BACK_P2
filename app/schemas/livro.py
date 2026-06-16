from decimal import Decimal
from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, ConfigDict


# ── Autor ────────────────────────────────────────────────────────────────────

class AutorBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=150, examples=["Machado de Assis"])
    biografia: Optional[str] = Field(None, max_length=2000)
    nacionalidade: Optional[str] = Field(None, max_length=80, examples=["Brasileiro"])


class AutorCreate(AutorBase):
    pass


class AutorUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=150)
    biografia: Optional[str] = Field(None, max_length=2000)
    nacionalidade: Optional[str] = Field(None, max_length=80)


class AutorResponse(AutorBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    criado_em: datetime
    atualizado_em: datetime


# ── Livro ─────────────────────────────────────────────────────────────────────

class LivroBase(BaseModel):
    titulo: str = Field(
        ..., min_length=2, max_length=250, examples=["Dom Casmurro"]
    )
    sinopse: Optional[str] = Field(None, max_length=3000)
    isbn: str = Field(..., min_length=10, max_length=20, examples=["978-3-16-148410-0"])
    preco: Decimal = Field(..., gt=0, decimal_places=2, examples=["59.90"])
    paginas: int = Field(default=0, ge=0, examples=[300])
    ano_publicacao: Optional[int] = Field(None, ge=1000, le=2100, examples=[1899])
    disponivel: bool = Field(default=True)
    autor_id: Optional[UUID] = None

    @field_validator("isbn")
    @classmethod
    def isbn_normalizado(cls, v: str) -> str:
        # remove hífens e espaços para padronização
        return v.replace("-", "").replace(" ", "").strip()

    @field_validator("preco")
    @classmethod
    def preco_positivo(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("O preço deve ser maior que zero.")
        return v


class LivroCreate(LivroBase):
    pass


class LivroUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=2, max_length=250)
    sinopse: Optional[str] = Field(None, max_length=3000)
    preco: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    paginas: Optional[int] = Field(None, ge=0)
    ano_publicacao: Optional[int] = Field(None, ge=1000, le=2100)
    disponivel: Optional[bool] = None
    autor_id: Optional[UUID] = None


class LivroResponse(LivroBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    criado_em: datetime
    atualizado_em: datetime
    autor: Optional[AutorResponse] = None


class RespostaPaginada(BaseModel):
    total: int
    pagina: int
    tamanho: int
    paginas: int
    itens: list[LivroResponse]
