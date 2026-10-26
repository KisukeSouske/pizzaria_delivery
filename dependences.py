from fastapi import Depends, HTTPException
from main import SECRET_KEY, ALGORITHM, oauth2_schema
from models import db
from sqlalchemy.orm import sessionmaker, Session
from models import Usuario
from jose import jwt, JWTError


def criar_sessao():
    try:
        Session = sessionmaker(bind=db)
        session = Session()
        yield session
    finally:
        session.close()


SESSION_DEPENDENCY = Depends(criar_sessao)


def verificar_token(
    token: str = Depends(oauth2_schema), session: Session = SESSION_DEPENDENCY
):
    try:
        dict_info = jwt.decode(token, SECRET_KEY, ALGORITHM)
        id_usuario = int(dict_info.get("sub"))
    except JWTError:
        raise HTTPException(
            status_code=401, detail="Acesso Negado, verifique a validade do token"
        )
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso Inválido")
    return usuario


TOKEN_DEPENDENCY = Depends(verificar_token)


def verificar_admin(usuario: Usuario = TOKEN_DEPENDENCY):
    if not usuario.admin:
        raise HTTPException(status_code=403, detail="Acesso restrito a administradores")
    return usuario
