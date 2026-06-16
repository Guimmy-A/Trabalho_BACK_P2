import pytest
from httpx import AsyncClient

LIVRO_BASE = {
    "titulo": "O Senhor dos Anéis",
    "isbn": "978-0-26-110351-1",
    "preco": "89.90",
    "paginas": 1200,
    "sinopse": "A épica jornada de Frodo Bolseiro para destruir o Um Anel.",
    "ano_publicacao": 1954,
    "disponivel": True,
}


async def cadastrar_livro(client: AsyncClient, dados: dict = None) -> dict:
    payload = dados or LIVRO_BASE.copy()
    resp = await client.post("/api/v1/livros/", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.mark.asyncio
async def test_cadastrar_livro_retorna_201(client: AsyncClient):
    resp = await client.post("/api/v1/livros/", json=LIVRO_BASE)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_cadastrar_livro_retorna_dados_corretos(client: AsyncClient):
    resp = await client.post("/api/v1/livros/", json=LIVRO_BASE)
    data = resp.json()

    assert data["titulo"] == LIVRO_BASE["titulo"]
    assert float(data["preco"]) == float(LIVRO_BASE["preco"])
    assert data["paginas"] == LIVRO_BASE["paginas"]
    assert data["disponivel"] is True
    assert "id" in data
    assert "criado_em" in data


@pytest.mark.asyncio
async def test_cadastrar_livro_isbn_normalizado(client: AsyncClient):
    payload = {**LIVRO_BASE, "isbn": "978-0-26-110351-1"}
    resp = await client.post("/api/v1/livros/", json=payload)
    assert resp.status_code == 201
    # ISBN deve ser armazenado sem hífens
    assert resp.json()["isbn"] == "9780261103511"


@pytest.mark.asyncio
async def test_cadastrar_livro_isbn_duplicado_retorna_409(client: AsyncClient):
    await cadastrar_livro(client)
    resp = await client.post("/api/v1/livros/", json=LIVRO_BASE)
    assert resp.status_code == 409
    assert "detalhe" in resp.json()


@pytest.mark.asyncio
async def test_cadastrar_livro_dados_invalidos_retorna_422(client: AsyncClient):
    payload = {"titulo": "X", "isbn": "123", "preco": "-5"}
    resp = await client.post("/api/v1/livros/", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_consultar_livro_existente_retorna_200(client: AsyncClient):
    livro = await cadastrar_livro(client)
    resp = await client.get(f"/api/v1/livros/{livro['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == livro["id"]


@pytest.mark.asyncio
async def test_consultar_livro_inexistente_retorna_404(client: AsyncClient):
    resp = await client.get("/api/v1/livros/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_listar_livros_retorna_200(client: AsyncClient):
    await cadastrar_livro(client)
    resp = await client.get("/api/v1/livros/")
    assert resp.status_code == 200
    data = resp.json()
    assert "total" in data
    assert "itens" in data
    assert "paginas" in data
    assert isinstance(data["itens"], list)


@pytest.mark.asyncio
async def test_listar_livros_paginacao(client: AsyncClient):
    for i in range(4):
        await cadastrar_livro(
            client,
            {**LIVRO_BASE, "isbn": f"97800000000{i:02d}", "titulo": f"Livro {i}"},
        )

    resp = await client.get("/api/v1/livros/?pagina=1&tamanho=2&apenas_disponiveis=false")
    data = resp.json()
    assert data["total"] == 4
    assert len(data["itens"]) == 2
    assert data["paginas"] == 2


@pytest.mark.asyncio
async def test_listar_livros_busca_por_titulo(client: AsyncClient):
    await cadastrar_livro(
        client,
        {**LIVRO_BASE, "titulo": "Duna", "isbn": "97800000001"},
    )
    await cadastrar_livro(
        client,
        {**LIVRO_BASE, "titulo": "Fundação", "isbn": "97800000002"},
    )

    resp = await client.get("/api/v1/livros/?busca=Duna")
    data = resp.json()
    assert data["total"] == 1
    assert data["itens"][0]["titulo"] == "Duna"


@pytest.mark.asyncio
async def test_atualizar_livro_retorna_200(client: AsyncClient):
    livro = await cadastrar_livro(client)
    resp = await client.patch(
        f"/api/v1/livros/{livro['id']}",
        json={"titulo": "O Senhor dos Anéis — Edição Especial", "preco": "129.90"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["titulo"] == "O Senhor dos Anéis — Edição Especial"
    assert float(data["preco"]) == 129.90


@pytest.mark.asyncio
async def test_atualizar_livro_inexistente_retorna_404(client: AsyncClient):
    resp = await client.patch(
        "/api/v1/livros/00000000-0000-0000-0000-000000000000",
        json={"titulo": "Qualquer"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_atualizar_livro_indisponivel(client: AsyncClient):
    livro = await cadastrar_livro(client)
    resp = await client.patch(
        f"/api/v1/livros/{livro['id']}",
        json={"disponivel": False},
    )
    assert resp.status_code == 200
    assert resp.json()["disponivel"] is False


@pytest.mark.asyncio
async def test_atualizar_paginas(client: AsyncClient):
    livro = await cadastrar_livro(client)
    resp = await client.patch(
        f"/api/v1/livros/{livro['id']}",
        json={"paginas": 1350},
    )
    assert resp.json()["paginas"] == 1350


@pytest.mark.asyncio
async def test_excluir_livro_retorna_204(client: AsyncClient):
    livro = await cadastrar_livro(client)
    resp = await client.delete(f"/api/v1/livros/{livro['id']}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_excluir_livro_inexistente_retorna_404(client: AsyncClient):
    resp = await client.delete("/api/v1/livros/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_livro_excluido_nao_encontrado_depois(client: AsyncClient):
    livro = await cadastrar_livro(client)
    await client.delete(f"/api/v1/livros/{livro['id']}")
    resp = await client.get(f"/api/v1/livros/{livro['id']}")
    assert resp.status_code == 404
