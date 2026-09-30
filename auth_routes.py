from fastapi import APIRouter, Depends, HTTPException
from models import Usuario
from dependences import criar_sessao
from main import bcrypt_context
from schemas import UsuarioSchema
from sqlalchemy.orm import Session

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
SESSION_DEPENDENCY = Depends(criar_sessao)

@auth_router.get("/")
async def home():
    """
    Essa é a rota padrão de autentificação do sistema
    """
    return "Sim, esta é a rota padrão"

@auth_router.post("/criar_conta")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session=SESSION_DEPENDENCY):

    usuario = session.query(Usuario).filter_by(email=usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="Já existe um usuário com este e-mail.")
    else:
        senha_cryptografada = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(usuario_schema.nome, usuario_schema.email, senha_cryptografada, usuario_schema.admin, usuario_schema.ativo) # pyright: ignore[reportArgumentType]
        session.add(novo_usuario)
        session.commit()
        return {"message": "Usuário cadastrado com sucesso!"}
    session.close()