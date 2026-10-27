from passlib.exc import UnknownHashError

from app.core.security import bcrypt_context
from app.models import Usuario


def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter_by(email=email).first()
    if not usuario:
        return None
    try:
        senha_confere = bcrypt_context.verify(senha, usuario.senha)
    except UnknownHashError:
        # Cadastros antigos gravaram a senha sem hash. O passlib não reconhece o
        # valor e levanta erro; sem hash válido não há como autenticar.
        return None
    if not senha_confere:
        return None
    return usuario
