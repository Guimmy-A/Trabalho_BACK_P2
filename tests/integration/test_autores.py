import pytest
from httpx import AsyncClient

AUTOR_BASE = {
    "nome": "J.R.R. Tolkien",
    "biografia": "John Ronald Reuel Tolkien foi um escritor e filólogo britânico.",
    "nacionalidade": "Britânico",
}

LIVRO_BASE = {
    "titulo": "O Hobbit",
    "isbn": "9780345339683",
    "preco": "49.90",
    "paginas": 310,
    "ano_publicacao": 1937,
}


async def cadastrar_autor(client: AsyncClient, dados: dict = None) -> dict:
    payload = dados or AUTOR_BASE.copy()
    resp = await client.post("/api/v1/autores/", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


@pytest.mark.asyncio
async def test_cadastrar_autor_retorna_201(client: AsyncClient):
    resp = await client.post("/api/v1/autores/", json=AUTOR_BASE)
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_cadastrar_autor_retorna_dados_corretos(client: AsyncClient):
    resp = await client.post("/api/v1/autores/", json=AUTOR_BASE)
    data = resp.json()
    assert data["nome"] == AUTOR_BASE["nome"]
    assert data["nacionalidade"] == AUTOR_BASE["nacionalidade"]
    assert "id" in data


@pytest.mark.asyncio
async def test_cadastrar_autor_duplicado_retorna_409(client: AsyncClient):
    await cadastrar_autor(client)
    resp = await client.post("/api/v1/autores/", json=AUTOR_BASE)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_listar_autores_retorna_200(client: AsyncClient):
    await cadastrar_autor(client)
    resp = await client.get("/api/v1/autores/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_consultar_autor_existente(client: AsyncClient):
    autor = await cadastrar_autor(client)
    resp = await client.get(f"/api/v1/autores/{autor['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == autor["id"]


@pytest.mark.asyncio
async def test_consultar_autor_inexistente_retorna_404(client: AsyncClient):
    resp = await client.get("/api/v1/autores/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_atualizar_autor_retorna_200(client: AsyncClient):
    autor = await cadastrar_autor(client)
    resp = await client.patch(
        f"/api/v1/autores/{autor['id']}",
        json={"nacionalidade": "Inglês"},
    )
    assert resp.status_code == 200
    assert resp.json()["nacionalidade"] == "Inglês"


@pytest.mark.asyncio
async def test_atualizar_autor_inexistente_retorna_404(client: AsyncClient):
    resp = await client.patch(
        "/api/v1/autores/00000000-0000-0000-0000-000000000000",
        json={"nome": "Qualquer"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_excluir_autor_retorna_204(client: AsyncClient):
    autor = await cadastrar_autor(client)
    resp = await client.delete(f"/api/v1/autores/{autor['id']}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_excluir_autor_inexistente_retorna_404(client: AsyncClient):
    resp = await client.delete("/api/v1/autores/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_cadastrar_livro_com_autor_valido(client: AsyncClient):
    autor = await cadastrar_autor(client)
    resp = await client.post(
        "/api/v1/livros/",
        json={**LIVRO_BASE, "autor_id": autor["id"]},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["autor"]["id"] == autor["id"]
    assert data["autor"]["nome"] == autor["nome"]


@pytest.mark.asyncio
async def test_cadastrar_livro_com_autor_inexistente_retorna_404(client: AsyncClient):
    resp = await client.post(
        "/api/v1/livros/",
        json={**LIVRO_BASE, "autor_id": "00000000-0000-0000-0000-000000000000"},
    )
    assert resp.status_code == 404
