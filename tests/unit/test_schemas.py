import pytest
from decimal import Decimal
from pydantic import ValidationError

from app.schemas.livro import LivroCreate, LivroUpdate, AutorCreate


class TestLivroCreateSchema:
    def test_isbn_normalizado_sem_hifens(self):
        livro = LivroCreate(
            titulo="Dom Casmurro",
            isbn="978-85-359-0277-5",
            preco=Decimal("45.00"),
            paginas=256,
        )
        assert livro.isbn == "9788535902775"

    def test_isbn_com_espacos_removidos(self):
        livro = LivroCreate(
            titulo="Dom Casmurro",
            isbn="  9788535902775  ",
            preco=Decimal("45.00"),
        )
        assert livro.isbn == "9788535902775"

    def test_preco_zero_invalido(self):
        with pytest.raises(ValidationError) as exc_info:
            LivroCreate(titulo="Livro", isbn="9788535902775", preco=Decimal("0.00"))
        assert "preco" in str(exc_info.value)

    def test_preco_negativo_invalido(self):
        with pytest.raises(ValidationError):
            LivroCreate(titulo="Livro", isbn="9788535902775", preco=Decimal("-10.00"))

    def test_titulo_muito_curto_invalido(self):
        with pytest.raises(ValidationError):
            LivroCreate(titulo="X", isbn="9788535902775", preco=Decimal("30.00"))

    def test_paginas_negativas_invalidas(self):
        with pytest.raises(ValidationError):
            LivroCreate(
                titulo="Livro Válido",
                isbn="9788535902775",
                preco=Decimal("30.00"),
                paginas=-5,
            )

    def test_ano_publicacao_invalido(self):
        with pytest.raises(ValidationError):
            LivroCreate(
                titulo="Livro",
                isbn="9788535902775",
                preco=Decimal("30.00"),
                ano_publicacao=500,
            )

    def test_livro_valido_criado(self):
        livro = LivroCreate(
            titulo="1984",
            isbn="9780451524935",
            preco=Decimal("35.00"),
            paginas=328,
            ano_publicacao=1949,
            sinopse="Distopia de George Orwell.",
        )
        assert livro.titulo == "1984"
        assert livro.preco == Decimal("35.00")
        assert livro.disponivel is True  # default


class TestLivroUpdateSchema:
    def test_update_parcial_so_titulo(self):
        update = LivroUpdate(titulo="Novo Título")
        dados = update.model_dump(exclude_unset=True)
        assert "titulo" in dados
        assert "preco" not in dados

    def test_update_vazio_valido(self):
        update = LivroUpdate()
        assert update.model_dump(exclude_unset=True) == {}

    def test_update_so_disponivel(self):
        update = LivroUpdate(disponivel=False)
        dados = update.model_dump(exclude_unset=True)
        assert dados == {"disponivel": False}


class TestAutorCreateSchema:
    def test_nome_muito_curto_invalido(self):
        with pytest.raises(ValidationError):
            AutorCreate(nome="AB")

    def test_autor_valido(self):
        autor = AutorCreate(
            nome="Clarice Lispector",
            nacionalidade="Brasileira",
            biografia="Uma das maiores escritoras brasileiras.",
        )
        assert autor.nome == "Clarice Lispector"

    def test_autor_sem_campos_opcionais(self):
        autor = AutorCreate(nome="Carlos Drummond")
        assert autor.biografia is None
        assert autor.nacionalidade is None
