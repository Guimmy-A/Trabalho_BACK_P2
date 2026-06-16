# 📚 API de Biblioteca

API REST para gerenciamento de acervo de **livros e autores**, desenvolvida com **FastAPI** e **PostgreSQL**, containerizada com **Docker** e testada com **Pytest**.

---

## 📋 Descrição do Projeto

A aplicação permite gerenciar um acervo bibliográfico com duas entidades relacionadas:

### Livro

| Campo            | Tipo     | Descrição                                   |
|-----------------|----------|---------------------------------------------|
| `id`             | UUID     | Identificador único (auto)                  |
| `titulo`         | string   | Título do livro (obrigatório)               |
| `sinopse`        | string   | Sinopse opcional                            |
| `isbn`           | string   | ISBN único, normalizado sem hífens          |
| `preco`          | decimal  | Preço (obrigatório, > 0)                    |
| `paginas`        | int      | Número de páginas (≥ 0)                    |
| `ano_publicacao` | int      | Ano entre 1000 e 2100                       |
| `disponivel`     | bool     | Se o livro está disponível no acervo        |
| `autor_id`       | UUID     | Referência opcional ao autor                |
| `criado_em`      | datetime | Timestamp de criação (auto)                 |
| `atualizado_em`  | datetime | Timestamp de atualização (auto)             |

### Autor

| Campo          | Tipo     | Descrição                         |
|---------------|----------|-----------------------------------|
| `id`           | UUID     | Identificador único (auto)        |
| `nome`         | string   | Nome do autor (único, obrigatório)|
| `biografia`    | string   | Biografia opcional                |
| `nacionalidade`| string   | Nacionalidade opcional            |
| `criado_em`    | datetime | Timestamp de criação (auto)       |
| `atualizado_em`| datetime | Timestamp de atualização (auto)   |

### Tecnologias

- **FastAPI** — framework web assíncrono de alta performance
- **SQLAlchemy 2.0 (async)** — ORM com suporte nativo a asyncio
- **PostgreSQL 16** — banco de dados relacional
- **asyncpg** — driver async para PostgreSQL
- **pydantic-settings** — configuração via variáveis de ambiente
- **Docker + Docker Compose** — containerização e orquestração
- **Pytest + HTTPX** — testes assíncronos

---

## 🚀 Execução da Aplicação

### Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Passo a passo

**1. Clone e entre na pasta:**

```bash
git clone <url-do-repositório>
cd api-biblioteca
```

**2. (Opcional) Configure as variáveis de ambiente:**

```bash
cp .env.example .env
# Edite o .env se necessário
```

**3. Suba os containers:**

```bash
docker compose up --build
```

A API estará disponível em `http://localhost:8000`.

**4. Documentação interativa:**

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

**5. Encerrar:**

```bash
docker compose down        # para os containers
docker compose down -v     # remove também o volume do banco
```

---

## 🔌 Endpoints da API

### Livros — `/api/v1/livros`

| Método  | Rota                  | Descrição                              |
|---------|-----------------------|----------------------------------------|
| POST    | `/`                   | Cadastrar livro                        |
| GET     | `/`                   | Listar livros (paginação + filtros)    |
| GET     | `/{id}`               | Consultar livro por ID                 |
| PATCH   | `/{id}`               | Atualizar livro parcialmente           |
| DELETE  | `/{id}`               | Excluir livro                          |

**Filtros disponíveis na listagem:**

| Parâmetro           | Tipo   | Padrão | Descrição                         |
|--------------------|--------|--------|-----------------------------------|
| `pagina`            | int    | 1      | Número da página                  |
| `tamanho`           | int    | 20     | Itens por página (máx. 100)       |
| `busca`             | string | —      | Busca por título, ISBN ou sinopse |
| `autor_id`          | UUID   | —      | Filtrar por autor                 |
| `apenas_disponiveis`| bool   | true   | Retornar só os disponíveis        |

### Autores — `/api/v1/autores`

| Método  | Rota       | Descrição                    |
|---------|------------|------------------------------|
| POST    | `/`        | Cadastrar autor              |
| GET     | `/`        | Listar todos os autores      |
| GET     | `/{id}`    | Consultar autor por ID       |
| PATCH   | `/{id}`    | Atualizar autor parcialmente |
| DELETE  | `/{id}`    | Excluir autor                |

### Exemplos com `curl`

**Cadastrar autor:**
```bash
curl -X POST http://localhost:8000/api/v1/autores/ \
  -H "Content-Type: application/json" \
  -d '{"nome": "Machado de Assis", "nacionalidade": "Brasileiro"}'
```

**Cadastrar livro com autor:**
```bash
curl -X POST http://localhost:8000/api/v1/livros/ \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Dom Casmurro",
    "isbn": "978-85-359-0277-5",
    "preco": "45.90",
    "paginas": 256,
    "ano_publicacao": 1899,
    "autor_id": "<uuid-do-autor>"
  }'
```

**Listar com busca e paginação:**
```bash
curl "http://localhost:8000/api/v1/livros/?busca=Dom&pagina=1&tamanho=10"
```

**Atualizar parcialmente:**
```bash
curl -X PATCH http://localhost:8000/api/v1/livros/<id> \
  -H "Content-Type: application/json" \
  -d '{"preco": "39.90", "disponivel": false}'
```

---

## 🧪 Execução dos Testes

Os testes utilizam **SQLite em memória via aiosqlite** — nenhum banco externo é necessário.

### Instalar dependências localmente

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
# ou: venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### Rodar os testes

```bash
pytest
```

### Rodar com verbose e sem cobertura

```bash
pytest -v --no-cov
```

### Rodar grupos específicos

```bash
pytest tests/unit/                      # apenas testes unitários de schemas
pytest tests/integration/test_livros.py # apenas livros
pytest tests/integration/test_autores.py
```

### Rodar testes dentro do Docker

```bash
docker compose run --rm test
```

---

## 🗂 Estrutura do Projeto

```
api-biblioteca/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── autores.py    # Rotas de autores
│   │       │   └── livros.py     # Rotas de livros
│   │       └── router.py
│   ├── core/
│   │   ├── config.py             # Settings via pydantic-settings
│   │   └── exceptions.py         # Exceções de domínio
│   ├── db/
│   │   └── session.py            # Engine async + get_db
│   ├── models/
│   │   └── livro.py              # Modelos ORM (Autor, Livro)
│   ├── repositories/
│   │   └── livro.py              # Acesso ao banco de dados
│   ├── schemas/
│   │   └── livro.py              # Schemas Pydantic + validações
│   ├── services/
│   │   └── livro.py              # Regras de negócio
│   └── main.py                   # App factory + lifespan
├── tests/
│   ├── conftest.py               # Fixtures de banco e cliente HTTP
│   ├── integration/
│   │   ├── test_health.py
│   │   ├── test_livros.py        # 17 casos de teste
│   │   └── test_autores.py       # 14 casos de teste
│   └── unit/
│       └── test_schemas.py       # 13 casos de teste
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

---

## ⚙️ Variáveis de Ambiente

| Variável            | Padrão              | Descrição                   |
|--------------------|---------------------|------------------------------|
| `APP_NAME`          | `API de Biblioteca` | Nome exibido no Swagger      |
| `APP_VERSION`       | `1.0.0`             | Versão da API                |
| `DEBUG`             | `false`             | Ativa logs SQL do SQLAlchemy |
| `API_V1_PREFIX`     | `/api/v1`           | Prefixo das rotas            |
| `POSTGRES_HOST`     | `localhost`         | Host do banco                |
| `POSTGRES_PORT`     | `5432`              | Porta do banco               |
| `POSTGRES_USER`     | `postgres`          | Usuário do banco             |
| `POSTGRES_PASSWORD` | `postgres`          | Senha do banco               |
| `POSTGRES_DB`       | `biblioteca_db`     | Nome do banco                |
| `PAGINA_PADRAO`     | `20`                | Itens por página padrão      |
| `PAGINA_MAXIMA`     | `100`               | Limite máximo de itens/página|
