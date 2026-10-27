import os

# Isola os testes do ambiente de desenvolvimento: estas variáveis precisam ser
# definidas ANTES de importar a aplicação (load_dotenv não sobrescreve o que já existe).
os.environ["SECRET_KEY"] = "chave-apenas-para-testes"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SQL_ECHO"] = "false"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app.api.dependencies import criar_sessao  # noqa: E402
from app.core.security import bcrypt_context, criar_token  # noqa: E402
from app.db.session import Base  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Pizza, Usuario  # noqa: E402

SENHA = "senha123"


@pytest.fixture(scope="session")
def senha_hash():
    # bcrypt é lento de propósito: calcula uma vez só para todos os testes.
    return bcrypt_context.hash(SENHA)


@pytest.fixture()
def session_factory():
    """Banco SQLite em memória, novo e vazio a cada teste."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine)
    engine.dispose()


@pytest.fixture()
def db(session_factory):
    """Sessão para testes que chamam services/models diretamente."""
    with session_factory() as session:
        yield session


@pytest.fixture()
def client(session_factory):
    """Cliente HTTP da API usando o banco em memória. O token é verificado de verdade."""

    def sessao_de_teste():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[criar_sessao] = sessao_de_teste
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def criar_usuario(session_factory, senha_hash):
    def _criar(nome, admin=False):
        with session_factory() as session:
            usuario = Usuario(nome, f"{nome}@teste.com", senha_hash, admin=admin)
            session.add(usuario)
            session.commit()
            return {
                "id": usuario.id,
                "email": usuario.email,
                "senha": SENHA,
                "headers": {"Authorization": f"Bearer {criar_token(usuario.id)}"},
            }

    return _criar


@pytest.fixture()
def ana(criar_usuario):
    return criar_usuario("ana")


@pytest.fixture()
def beto(criar_usuario):
    return criar_usuario("beto")


@pytest.fixture()
def admin(criar_usuario):
    return criar_usuario("admin", admin=True)


@pytest.fixture()
def pizzas(session_factory):
    """Catálogo com 2 pizzas ativas e 1 desativada. Devolve {chave: id}."""
    with session_factory() as session:
        catalogo = {
            "mussarela": Pizza("Mussarela", 35.5),
            "calabresa": Pizza("Calabresa", 40.0),
            "portuguesa": Pizza("Portuguesa", 38.0, ativo=False),
        }
        session.add_all(catalogo.values())
        session.commit()
        return {chave: pizza.id for chave, pizza in catalogo.items()}
