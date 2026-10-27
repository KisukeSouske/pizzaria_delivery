from app.core.security import bcrypt_context
from app.models import Usuario


def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter_by(email=email).first()
    if not usuario or not bcrypt_context.verify(senha, usuario.senha):
        return None
    return usuario
