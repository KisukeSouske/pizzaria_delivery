from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException
from jose import jwt

from app.core.config import ALGORITHM, SECRET_KEY
from app.core.security import bcrypt_context, criar_token
from app.models import Carrinho, ItemPedido, Pedido, Usuario
from app.services.auth import autenticar_usuario
from app.services.orders import (
    buscar_carrinho,
    buscar_pedido,
    calcular_total,
)

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------


def novo_carrinho(client, usuario):
    resposta = client.post("/orders/carrinho", headers=usuario["headers"])
    assert resposta.status_code == 201
    return resposta.json()["id"]


def adicionar(client, usuario, id_carrinho, id_pizza, quantidade=1):
    return client.post(
        f"/orders/carrinho/{id_carrinho}/itens",
        json={"id_pizza": id_pizza, "quantidade": quantidade},
        headers=usuario["headers"],
    )


def fazer_pedido(client, usuario, itens):
    """Cria um carrinho com `itens` [(id_pizza, quantidade)] e faz o checkout."""
    id_carrinho = novo_carrinho(client, usuario)
    for id_pizza, quantidade in itens:
        adicionar(client, usuario, id_carrinho, id_pizza, quantidade)
    resposta = client.post(
        "/orders/pedido", json={"carrinho": id_carrinho}, headers=usuario["headers"]
    )
    assert resposta.status_code == 201
    return resposta.json()


# ----------------------------------------------------------------------------
# Unidade: segurança e models
# ----------------------------------------------------------------------------


class TestSeguranca:
    def test_token_guarda_o_id_do_usuario_e_expira_no_futuro(self):
        dados = jwt.decode(criar_token(7), SECRET_KEY, ALGORITHM)

        assert dados["sub"] == "7"
        assert dados["exp"] > datetime.now(timezone.utc).timestamp()

    def test_token_respeita_a_duracao_informada(self):
        agora = datetime.now(timezone.utc).timestamp()

        dados = jwt.decode(criar_token(1, timedelta(days=7)), SECRET_KEY, ALGORITHM)

        assert dados["exp"] - agora == pytest.approx(7 * 24 * 3600, abs=5)

    def test_senha_e_guardada_como_hash_verificavel(self):
        hash_da_senha = bcrypt_context.hash("segredo")

        assert hash_da_senha != "segredo"
        assert bcrypt_context.verify("segredo", hash_da_senha)
        assert not bcrypt_context.verify("outra", hash_da_senha)


class TestItemPedido:
    def test_preco_do_item_e_unitario_vezes_quantidade(self):
        item = ItemPedido(carrinho=None, pizza="Calabresa", preco_unitario=40, quantidade=3)

        assert item.preco == 120

    def test_preco_do_item_e_arredondado_em_centavos(self):
        # 10.1 * 3 = 30.299999999999997 em ponto flutuante
        item = ItemPedido(carrinho=None, pizza="X", preco_unitario=10.1, quantidade=3)

        assert item.preco == 30.3

    def test_calcular_total(self):
        assert calcular_total([]) == 0
        itens = [
            ItemPedido(carrinho=None, pizza="A", preco_unitario=0.1, quantidade=1),
            ItemPedido(carrinho=None, pizza="B", preco_unitario=0.2, quantidade=1),
        ]
        assert calcular_total(itens) == 0.3  # 0.1 + 0.2 puro daria 0.30000000000000004


# ----------------------------------------------------------------------------
# Unidade: services
# ----------------------------------------------------------------------------


class TestServices:
    def test_autenticar_usuario(self, db, ana):
        assert autenticar_usuario(ana["email"], ana["senha"], db).id == ana["id"]
        assert autenticar_usuario(ana["email"], "senha-errada", db) is None
        assert autenticar_usuario("ninguem@teste.com", ana["senha"], db) is None

    def test_buscar_carrinho_valida_existencia_e_dono(self, db, ana, beto):
        carrinho = Carrinho(usuario=ana["id"])
        db.add(carrinho)
        db.commit()
        dono, outro = db.get(Usuario, ana["id"]), db.get(Usuario, beto["id"])

        assert buscar_carrinho(carrinho.id, dono, db).id == carrinho.id
        with pytest.raises(HTTPException) as erro:
            buscar_carrinho(carrinho.id, outro, db)
        assert erro.value.status_code == 403
        with pytest.raises(HTTPException) as erro:
            buscar_carrinho(999, dono, db)
        assert erro.value.status_code == 404

    def test_buscar_pedido_permite_dono_e_admin_mas_nao_outro_usuario(
        self, db, ana, beto, admin
    ):
        pedido = Pedido(usuario=ana["id"], preco_total=10, status="AGUARDANDO_PGTO")
        db.add(pedido)
        db.commit()

        def usuario(dados):
            return db.get(Usuario, dados["id"])

        assert buscar_pedido(pedido.id, usuario(ana), db).id == pedido.id
        assert buscar_pedido(pedido.id, usuario(admin), db).id == pedido.id
        with pytest.raises(HTTPException) as erro:
            buscar_pedido(pedido.id, usuario(beto), db)
        assert erro.value.status_code == 403
        with pytest.raises(HTTPException) as erro:
            buscar_pedido(999, usuario(ana), db)
        assert erro.value.status_code == 404


# ----------------------------------------------------------------------------
# API: autenticação
# ----------------------------------------------------------------------------


class TestAuth:
    def test_criar_conta_guarda_a_senha_com_hash(self, client, session_factory):
        resposta = client.post(
            "/auth/criar_conta",
            json={"nome": "Cris", "email": "cris@teste.com", "senha": "abc123"},
        )

        assert resposta.status_code == 200
        with session_factory() as session:
            usuario = session.query(Usuario).filter_by(email="cris@teste.com").one()
            assert usuario.senha != "abc123"
            assert bcrypt_context.verify("abc123", usuario.senha)
            assert usuario.admin is False

    def test_criar_conta_com_email_repetido_retorna_400(self, client, ana):
        resposta = client.post(
            "/auth/criar_conta",
            json={"nome": "Outra Ana", "email": ana["email"], "senha": "x"},
        )

        assert resposta.status_code == 400

    def test_login_devolve_access_e_refresh_token(self, client, ana):
        resposta = client.post(
            "/auth/login", json={"email": ana["email"], "senha": ana["senha"]}
        )

        assert resposta.status_code == 200
        corpo = resposta.json()
        assert corpo["token_type"] == "Bearer"
        assert jwt.decode(corpo["access_token"], SECRET_KEY, ALGORITHM)["sub"] == str(
            ana["id"]
        )
        assert corpo["refresh_token"]

    @pytest.mark.parametrize(
        "email, senha",
        [("ana@teste.com", "senha-errada"), ("ninguem@teste.com", "senha123")],
    )
    def test_login_com_credenciais_invalidas_retorna_400(
        self, client, ana, email, senha
    ):
        resposta = client.post("/auth/login", json={"email": email, "senha": senha})

        assert resposta.status_code == 400

    def test_login_form_aceita_username_e_password(self, client, ana):
        resposta = client.post(
            "/auth/login-form",
            data={"username": ana["email"], "password": ana["senha"]},
        )

        assert resposta.status_code == 200
        assert "access_token" in resposta.json()

    def test_refresh_gera_novo_access_token(self, client, ana):
        resposta = client.get("/auth/refresh", headers=ana["headers"])

        assert resposta.status_code == 200
        assert resposta.json()["token_type"] == "Bearer"
        assert resposta.json()["access_token"]

    @pytest.mark.parametrize(
        "metodo, rota",
        [
            ("get", "/auth/refresh"),
            ("get", "/orders/"),
            ("post", "/orders/carrinho"),
            ("get", "/orders/carrinho/1"),
            ("get", "/orders/pedido/1"),
            ("get", "/pizzas/todas"),
        ],
    )
    def test_rota_protegida_sem_token_retorna_401(self, client, metodo, rota):
        assert getattr(client, metodo)(rota).status_code == 401

    def test_token_invalido_retorna_401(self, client):
        resposta = client.get("/orders/", headers={"Authorization": "Bearer lixo"})

        assert resposta.status_code == 401

    def test_token_expirado_retorna_401(self, client, ana):
        expirado = criar_token(ana["id"], timedelta(seconds=-5))

        resposta = client.get("/orders/", headers={"Authorization": f"Bearer {expirado}"})

        assert resposta.status_code == 401

    def test_token_de_usuario_inexistente_retorna_401(self, client):
        token = criar_token(9999)

        resposta = client.get("/orders/", headers={"Authorization": f"Bearer {token}"})

        assert resposta.status_code == 401


# ----------------------------------------------------------------------------
# API: pizzas
# ----------------------------------------------------------------------------


class TestPizzas:
    def test_cardapio_publico_lista_so_ativas_em_ordem_alfabetica(self, client, pizzas):
        resposta = client.get("/pizzas/")

        assert resposta.status_code == 200
        assert [p["nome"] for p in resposta.json()] == ["Calabresa", "Mussarela"]

    def test_catalogo_completo_e_so_para_admin(self, client, pizzas, ana, admin):
        assert client.get("/pizzas/todas", headers=ana["headers"]).status_code == 403

        resposta = client.get("/pizzas/todas", headers=admin["headers"])

        assert resposta.status_code == 200
        assert len(resposta.json()) == 3  # inclui a desativada

    def test_admin_cria_pizza(self, client, admin):
        resposta = client.post(
            "/pizzas/", json={"nome": "Pepperoni", "preco": 45}, headers=admin["headers"]
        )

        assert resposta.status_code == 201
        assert resposta.json()["nome"] == "Pepperoni"
        assert resposta.json()["ativo"] is True

    def test_usuario_comum_nao_cria_pizza(self, client, ana):
        resposta = client.post(
            "/pizzas/", json={"nome": "Pepperoni", "preco": 45}, headers=ana["headers"]
        )

        assert resposta.status_code == 403

    def test_nome_repetido_e_recusado_sem_diferenciar_maiusculas(
        self, client, admin, pizzas
    ):
        resposta = client.post(
            "/pizzas/", json={"nome": "CALABRESA", "preco": 41}, headers=admin["headers"]
        )

        assert resposta.status_code == 400

    @pytest.mark.parametrize(
        "corpo",
        [
            {"nome": "Zero", "preco": 0},
            {"nome": "Negativa", "preco": -5},
            {"nome": "", "preco": 10},
        ],
    )
    def test_dados_invalidos_retornam_422(self, client, admin, corpo):
        resposta = client.post("/pizzas/", json=corpo, headers=admin["headers"])

        assert resposta.status_code == 422

    def test_atualizar_um_campo_preserva_os_outros(self, client, admin, pizzas):
        resposta = client.patch(
            f"/pizzas/{pizzas['calabresa']}", json={"preco": 45}, headers=admin["headers"]
        )

        assert resposta.status_code == 200
        assert resposta.json()["preco"] == 45
        assert resposta.json()["nome"] == "Calabresa"
        assert resposta.json()["ativo"] is True

    def test_pizza_desativada_sai_do_cardapio_publico(self, client, admin, pizzas):
        client.patch(
            f"/pizzas/{pizzas['calabresa']}",
            json={"ativo": False},
            headers=admin["headers"],
        )

        nomes = [p["nome"] for p in client.get("/pizzas/").json()]

        assert nomes == ["Mussarela"]

    def test_renomear_para_nome_de_outra_pizza_retorna_400(self, client, admin, pizzas):
        resposta = client.patch(
            f"/pizzas/{pizzas['mussarela']}",
            json={"nome": "calabresa"},
            headers=admin["headers"],
        )

        assert resposta.status_code == 400

    def test_manter_o_proprio_nome_e_permitido(self, client, admin, pizzas):
        resposta = client.patch(
            f"/pizzas/{pizzas['mussarela']}",
            json={"nome": "Mussarela", "preco": 36},
            headers=admin["headers"],
        )

        assert resposta.status_code == 200

    def test_usuario_comum_nao_atualiza_pizza(self, client, ana, pizzas):
        resposta = client.patch(
            f"/pizzas/{pizzas['calabresa']}", json={"preco": 1}, headers=ana["headers"]
        )

        assert resposta.status_code == 403

    def test_atualizar_pizza_inexistente_retorna_404(self, client, admin):
        resposta = client.patch("/pizzas/999", json={"preco": 1}, headers=admin["headers"])

        assert resposta.status_code == 404


# ----------------------------------------------------------------------------
# API: carrinho
# ----------------------------------------------------------------------------


class TestCarrinho:
    def test_carrinho_novo_nasce_vazio(self, client, ana):
        id_carrinho = novo_carrinho(client, ana)

        resposta = client.get(f"/orders/carrinho/{id_carrinho}", headers=ana["headers"])

        assert resposta.status_code == 200
        assert resposta.json()["itens"] == []
        assert resposta.json()["preco_total"] == 0

    def test_carrinho_de_outro_usuario_retorna_403(self, client, ana, beto):
        id_carrinho = novo_carrinho(client, ana)

        resposta = client.get(f"/orders/carrinho/{id_carrinho}", headers=beto["headers"])

        assert resposta.status_code == 403

    def test_carrinho_inexistente_retorna_404(self, client, ana):
        assert client.get("/orders/carrinho/999", headers=ana["headers"]).status_code == 404

    def test_adicionar_item_calcula_preco_e_total(self, client, ana, pizzas):
        id_carrinho = novo_carrinho(client, ana)

        resposta = adicionar(client, ana, id_carrinho, pizzas["calabresa"], 2)

        assert resposta.status_code == 201
        corpo = resposta.json()
        assert len(corpo["itens"]) == 1
        assert corpo["itens"][0]["pizza"] == "Calabresa"
        assert corpo["itens"][0]["preco_unitario"] == 40.0
        assert corpo["itens"][0]["preco"] == 80.0
        assert corpo["preco_total"] == 80.0

    def test_adicionar_a_mesma_pizza_soma_a_quantidade_pedida(self, client, ana, pizzas):
        id_carrinho = novo_carrinho(client, ana)
        adicionar(client, ana, id_carrinho, pizzas["calabresa"], 2)

        corpo = adicionar(client, ana, id_carrinho, pizzas["calabresa"], 3).json()

        assert len(corpo["itens"]) == 1  # não duplica a linha
        assert corpo["itens"][0]["quantidade"] == 5  # soma 3, e não apenas +1
        assert corpo["itens"][0]["preco"] == 200.0  # preço da linha recalculado
        assert corpo["preco_total"] == 200.0

    def test_pizzas_diferentes_viram_linhas_diferentes(self, client, ana, pizzas):
        id_carrinho = novo_carrinho(client, ana)
        adicionar(client, ana, id_carrinho, pizzas["calabresa"], 2)

        corpo = adicionar(client, ana, id_carrinho, pizzas["mussarela"], 1).json()

        assert [i["pizza"] for i in corpo["itens"]] == ["Calabresa", "Mussarela"]
        assert corpo["preco_total"] == 115.5

    def test_quantidade_deve_ser_maior_que_zero(self, client, ana, pizzas):
        id_carrinho = novo_carrinho(client, ana)

        for quantidade in (0, -1):
            resposta = adicionar(client, ana, id_carrinho, pizzas["calabresa"], quantidade)
            assert resposta.status_code == 422

    def test_pizza_inexistente_ou_desativada_retorna_404(self, client, ana, pizzas):
        id_carrinho = novo_carrinho(client, ana)

        assert adicionar(client, ana, id_carrinho, 999).status_code == 404
        assert adicionar(client, ana, id_carrinho, pizzas["portuguesa"]).status_code == 404

    def test_nao_adiciona_item_no_carrinho_de_outro_usuario(self, client, ana, beto, pizzas):
        id_carrinho = novo_carrinho(client, ana)

        resposta = adicionar(client, beto, id_carrinho, pizzas["calabresa"])

        assert resposta.status_code == 403

    def test_item_mantem_o_preco_da_epoca_se_o_catalogo_mudar(
        self, client, ana, admin, pizzas
    ):
        id_carrinho = novo_carrinho(client, ana)
        adicionar(client, ana, id_carrinho, pizzas["calabresa"], 1)

        client.patch(
            f"/pizzas/{pizzas['calabresa']}", json={"preco": 99}, headers=admin["headers"]
        )
        corpo = client.get(f"/orders/carrinho/{id_carrinho}", headers=ana["headers"]).json()

        assert corpo["itens"][0]["preco_unitario"] == 40.0
        assert corpo["preco_total"] == 40.0

    def test_remover_item_atualiza_o_total(self, client, ana, pizzas):
        id_carrinho = novo_carrinho(client, ana)
        adicionar(client, ana, id_carrinho, pizzas["calabresa"], 2)
        corpo = adicionar(client, ana, id_carrinho, pizzas["mussarela"], 1).json()
        id_mussarela = corpo["itens"][1]["id"]

        resposta = client.delete(
            f"/orders/carrinho/{id_carrinho}/itens/{id_mussarela}", headers=ana["headers"]
        )

        assert resposta.status_code == 200
        assert [i["pizza"] for i in resposta.json()["itens"]] == ["Calabresa"]
        assert resposta.json()["preco_total"] == 80.0

    def test_remover_item_inexistente_retorna_404(self, client, ana):
        id_carrinho = novo_carrinho(client, ana)

        resposta = client.delete(
            f"/orders/carrinho/{id_carrinho}/itens/999", headers=ana["headers"]
        )

        assert resposta.status_code == 404

    def test_nao_remove_item_de_outro_usuario(self, client, ana, beto, pizzas):
        id_carrinho = novo_carrinho(client, ana)
        id_item = adicionar(client, ana, id_carrinho, pizzas["calabresa"]).json()["itens"][0]["id"]

        resposta = client.delete(
            f"/orders/carrinho/{id_carrinho}/itens/{id_item}", headers=beto["headers"]
        )

        assert resposta.status_code == 403


# ----------------------------------------------------------------------------
# API: pedidos (checkout, consulta e cancelamento)
# ----------------------------------------------------------------------------


class TestPedidos:
    def test_checkout_cria_pedido_e_consome_o_carrinho(self, client, ana, pizzas):
        id_carrinho = novo_carrinho(client, ana)
        adicionar(client, ana, id_carrinho, pizzas["calabresa"], 2)
        adicionar(client, ana, id_carrinho, pizzas["mussarela"], 1)

        resposta = client.post(
            "/orders/pedido", json={"carrinho": id_carrinho}, headers=ana["headers"]
        )

        assert resposta.status_code == 201
        pedido = resposta.json()
        assert pedido["status"] == "AGUARDANDO_PGTO"
        assert pedido["preco_total"] == 115.5
        assert [i["pizza"] for i in pedido["itens"]] == ["Calabresa", "Mussarela"]
        # o carrinho foi descartado e os itens passaram para o pedido
        carrinho = client.get(f"/orders/carrinho/{id_carrinho}", headers=ana["headers"])
        assert carrinho.status_code == 404

    def test_checkout_de_carrinho_vazio_retorna_400(self, client, ana):
        id_carrinho = novo_carrinho(client, ana)

        resposta = client.post(
            "/orders/pedido", json={"carrinho": id_carrinho}, headers=ana["headers"]
        )

        assert resposta.status_code == 400

    def test_checkout_de_carrinho_alheio_ou_inexistente(self, client, ana, beto, pizzas):
        id_carrinho = novo_carrinho(client, ana)
        adicionar(client, ana, id_carrinho, pizzas["calabresa"])

        alheio = client.post(
            "/orders/pedido", json={"carrinho": id_carrinho}, headers=beto["headers"]
        )
        inexistente = client.post(
            "/orders/pedido", json={"carrinho": 999}, headers=ana["headers"]
        )

        assert alheio.status_code == 403
        assert inexistente.status_code == 404

    def test_dono_e_admin_veem_o_pedido_mas_outro_usuario_nao(
        self, client, ana, beto, admin, pizzas
    ):
        id_pedido = fazer_pedido(client, ana, [(pizzas["calabresa"], 1)])["id"]
        rota = f"/orders/pedido/{id_pedido}"

        assert client.get(rota, headers=ana["headers"]).status_code == 200
        assert client.get(rota, headers=admin["headers"]).status_code == 200
        assert client.get(rota, headers=beto["headers"]).status_code == 403
        assert client.get("/orders/pedido/999", headers=ana["headers"]).status_code == 404

    def test_usuario_lista_so_os_proprios_pedidos_e_admin_lista_todos(
        self, client, ana, beto, admin, pizzas
    ):
        id_ana = fazer_pedido(client, ana, [(pizzas["calabresa"], 1)])["id"]
        id_beto = fazer_pedido(client, beto, [(pizzas["mussarela"], 1)])["id"]

        def ids(usuario):
            return [p["id"] for p in client.get("/orders/", headers=usuario["headers"]).json()]

        assert ids(ana) == [id_ana]
        assert ids(beto) == [id_beto]
        assert ids(admin) == [id_ana, id_beto]

    def test_dono_cancela_o_pedido(self, client, session_factory, ana, pizzas):
        id_pedido = fazer_pedido(client, ana, [(pizzas["calabresa"], 1)])["id"]

        resposta = client.post(
            f"/orders/pedido/cancelar/{id_pedido}", headers=ana["headers"]
        )

        assert resposta.status_code == 200
        assert str(id_pedido) in resposta.json()["mensagem"]
        assert resposta.json()["pedido"]["status"] == "CANCELADO"
        # gravado como texto simples (regressão: já foi gravado como tupla)
        with session_factory() as session:
            assert session.get(Pedido, id_pedido).status == "CANCELADO"
        consulta = client.get(f"/orders/pedido/{id_pedido}", headers=ana["headers"])
        assert consulta.json()["status"] == "CANCELADO"

    def test_admin_cancela_pedido_de_qualquer_usuario(self, client, ana, admin, pizzas):
        id_pedido = fazer_pedido(client, ana, [(pizzas["calabresa"], 1)])["id"]

        resposta = client.post(
            f"/orders/pedido/cancelar/{id_pedido}", headers=admin["headers"]
        )

        assert resposta.status_code == 200

    def test_outro_usuario_nao_cancela_o_pedido(self, client, ana, beto, pizzas):
        id_pedido = fazer_pedido(client, ana, [(pizzas["calabresa"], 1)])["id"]

        resposta = client.post(
            f"/orders/pedido/cancelar/{id_pedido}", headers=beto["headers"]
        )

        assert resposta.status_code == 401
        consulta = client.get(f"/orders/pedido/{id_pedido}", headers=ana["headers"])
        assert consulta.json()["status"] == "AGUARDANDO_PGTO"

    def test_cancelar_pedido_inexistente_retorna_400(self, client, ana):
        resposta = client.post("/orders/pedido/cancelar/999", headers=ana["headers"])

        assert resposta.status_code == 400
