from decimal import Decimal
from typing import Optional
import uuid
from datetime import datetime

from sqlalchemy import (
    Numeric,
    String,
    Text,
    Boolean,
    Integer,
    SmallInteger,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base


class Autor(Base):
    __tablename__ = "autores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(
        String(150), nullable=False, unique=True, index=True
    )
    biografia: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    nacionalidade: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    livros: Mapped[list["Livro"]] = relationship(
        "Livro", back_populates="autor", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Autor(id={self.id}, nome={self.nome!r})>"


class Livro(Base):
    __tablename__ = "livros"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    titulo: Mapped[str] = mapped_column(String(250), nullable=False, index=True)
    sinopse: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    isbn: Mapped[str] = mapped_column(
        String(20), nullable=False, unique=True, index=True
    )
    preco: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False
    )
    paginas: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ano_publicacao: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    disponivel: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    autor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("autores.id", ondelete="SET NULL"),
        nullable=True,
    )
    criado_em: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), nullable=False
    )

    autor: Mapped[Optional[Autor]] = relationship(
        "Autor", back_populates="livros", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Livro(id={self.id}, titulo={self.titulo!r}, isbn={self.isbn!r})>"
