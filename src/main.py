from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends, Path, Query
from sqlmodel import Session, select

from src.schemas import (
    CriarPessoa,
    Pessoa,
    PessoaPublica,
    PessoaAtualizar,
    Msg
)

from src.database import get_session, create_and_db
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_and_db()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="API"
)


SessionDP = Annotated[
    Session,
    Depends(get_session)
]


app = FastAPI(lifespan=lifespan,title='API')
SessionDP = Annotated[Session,Depends(get_session)]

@app.post("/criar/",tags=['Criar usuário'],response_model=PessoaPublica)
def criar_usuario(pessoa:CriarPessoa,session:SessionDP):
    statement = select(Pessoa).where(Pessoa.email == pessoa.email)
    pessoa_existente = session.exec(statement).first()
    if pessoa_existente:
        raise HTTPException(status_code=409,detail="esse email ja foi cadastrado!")
    validar = Pessoa.model_validate(pessoa)
    session.add(validar)
    session.commit()
    session.refresh(validar)
    return validar

@app.get("/listar/usuarios",tags=['Listar Usuários'],response_model=list[PessoaPublica])
def listar_todos(session:SessionDP,
            offset:Annotated[int,Query(ge=1)],
            limit:Annotated[int,Query(le=100)] = 100):
    pessoas = session.exec(select(Pessoa).offset(offset).limit(limit)).all()
    return pessoas

@app.get("/buscar/nome",response_model=list[PessoaPublica],tags=['Buscar por nome'])
def buscar_nome_usuario(session:SessionDP,
            nome:Annotated[str,
            Query(min_length=3,max_length=50)]):
    statement = select(Pessoa).where(Pessoa.nome == nome)
    resultado = session.exec(statement).all()
    return resultado

@app.get("/buscar/usuario/{id_usuario}",tags=['Buscar usuário'],response_model=PessoaPublica)
def buscar_id_usuario(id_usuario:Annotated[int,
            Path(title="ID a ser buscado",ge=1)],
            session:SessionDP):
    get_usuario = session.get(Pessoa,id_usuario)
    if not get_usuario:
        raise HTTPException(status_code=404,detail='Usuário não encontrado')
    return get_usuario

@app.patch("/atualizar/{buscar_id}",response_model=PessoaPublica,tags=['Atualizar campos do usuário'])
def atualizar_user(buscar_id:Annotated[int,
             Path(title="Id do item",ge=1)],
             session:SessionDP,pessoa:PessoaAtualizar):
    buscar_usuario = session.get(Pessoa,buscar_id)
    if not buscar_usuario:
        raise HTTPException(status_code=404,detail="Usuário não encontrado")

    #1- não colocar email já registrado no banco ( outro usuário pode estar usando
    2#- #verificar se o email que o usuario digitou na api é o mesmo que esta no banco de dados e  se o id do usuario é diferente
    #se for o email esta em uso
    
    pessoa_db = pessoa.model_dump(exclude_unset=True)
    statement = select(Pessoa).where(Pessoa.email== pessoa.email,Pessoa.id != buscar_usuario.id)
    pessoa_existente = session.exec(statement).first()
    if pessoa_existente:
        raise HTTPException(status_code=409,detail="Email em uso!")

    buscar_usuario.sqlmodel_update(pessoa_db)
    session.add(buscar_usuario)
    session.commit()
    session.refresh(buscar_usuario)
    return buscar_usuario

@app.delete("/deletar/{buscar_id}",tags=['Remover usuário'],response_model=Msg)
def deletar_user(buscar_id:Annotated[int,Path(ge=1)],session:SessionDP):
    buscar_usuario = session.get(Pessoa,buscar_id)
    if not buscar_usuario:
        raise HTTPException(status_code=404,detail='Usuário não encontrado')
    session.delete(buscar_usuario)
    session.commit()
    return Msg(mensagem="Usuário deletado com sucesso!")
    


    

    











