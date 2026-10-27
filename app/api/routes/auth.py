from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import criar_sessao, verificar_token
from app.core.security import bcrypt_context, criar_token
from app.models import Usuario
from app.schemas import LoginSchema, UsuarioSchema
from app.services.auth import autenticar_usuario

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
SESSION_DEPENDENCY = Depends(criar_sessao)


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


@auth_router.post("/login-form")
async def login_form(
    dados_formulario: OAuth2PasswordRequestForm = Depends(),
    session: Session = SESSION_DEPENDENCY,
):

    usuario = autenticar_usuario(
        dados_formulario.username, dados_formulario.password, session
    )
    if not usuario:
        raise HTTPException(
            status_code=400, detail="Usuário não encontrado ou credenciais inválidas."
        )
    else:
        access_token = criar_token(usuario.id)
        return {
            "access_token": access_token,
            "token_type": "Bearer",
        }


@auth_router.get("/refresh")
async def use_refresh_token(usuario: Usuario = Depends(verificar_token)):
    access_token = criar_token(usuario.id)
    return {
        "access_token": access_token,
        "token_type": "Bearer",
    }
