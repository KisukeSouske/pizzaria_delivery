from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependences import criar_sessao
from main import bcrypt_context, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY
from schemas import UsuarioSchema, LoginSchema
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
SESSION_DEPENDENCY = Depends(criar_sessao)


def criar_token(id_usuario, duracao=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao
    dict_info = {"sub": id_usuario, "exp": data_expiracao}
    jwt_codificado = jwt.encode(dict_info, SECRET_KEY, ALGORITHM)
    return jwt_codificado


def autenticar_usuario(email, senha, session):
    usuario = session.query(Usuario).filter_by(email=email).first()
    if not usuario or not bcrypt_context.verify(senha, usuario.senha):
        return None
    return usuario


@auth_router.get("/")
async def home():
    """
    Essa é a rota padrão de autentificação do sistema
    """
    return "Sim, esta é a rota padrão"


@auth_router.post("/criar_conta")
async def criar_conta(
    usuario_schema: UsuarioSchema, session: Session = SESSION_DEPENDENCY
):
    usuario = session.query(Usuario).filter_by(email=usuario_schema.email).first()
    if usuario:
        raise HTTPException(
            status_code=400, detail="Já existe um usuário com este e-mail."
        )
    else:
        senha_cryptografada = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(
            usuario_schema.nome,
            usuario_schema.email,
            senha_cryptografada,
        )  # pyright: ignore[reportArgumentType]
        session.add(novo_usuario)
        session.commit()
        return {"message": "Usuário cadastrado com sucesso!"}
    session.close()


@auth_router.post("/login")
async def login(login_schema: LoginSchema, session: Session = SESSION_DEPENDENCY):

    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    if not usuario:
        raise HTTPException(
            status_code=400, detail="Usuário não encontrado ou credenciais inválidas."
        )
    else:
        access_token = criar_token(usuario.id)
        refresh_token = criar_token(usuario.id, timedelta(days=7))
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
        }
