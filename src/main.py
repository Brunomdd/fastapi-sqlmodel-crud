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

SessionDP = Annotated[
    Session,
    Depends(get_session)
]

app = FastAPI(lifespan=lifespan,title='API')

IdUsuario = Annotated[int,Path(title="ID do item",ge=1)]
NomeUsuario = Annotated[str,Query(pattern=r"^[^*!#()%^@]+$",min_length=3,max_length=50)]

@app.post("/usuarios/criar",tags=['Criar usuário'],response_model=PessoaPublica)
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

@app.get("/usuarios/listar",tags=['Listar Usuários'],response_model=list[PessoaPublica])
def listar_todos(session:SessionDP, 
            offset:Annotated[int,Query(ge=0)] = 0,
            limit:Annotated[int,Query(le=100)] = 100):
    pessoas = session.exec(select(Pessoa).offset(offset).limit(limit)).all()
    return pessoas

@app.get("/usuarios/nome",response_model=list[PessoaPublica],tags=['Buscar por nome'])
def buscar_nome_usuario(session:SessionDP,nome:NomeUsuario):
    statement = select(Pessoa).where(Pessoa.nome == nome)
    resultado = session.exec(statement).all()
    return resultado

@app.get("/usuarios/buscar/parcial",response_model=list[PessoaPublica],tags=["Busca parcial por nome"])
def busca_parcial(session:SessionDP
                  ,nome:NomeUsuario,offset:Annotated[int,Query(ge=0)] = 0,
                  limit:Annotated[int,Query(le=100)]=100):
    statement = select(Pessoa).where(Pessoa.nome.contains(nome)).offset(offset).limit(limit)
    resultado = session.exec(statement).all()
    return resultado

@app.get("/usuarios/{id_usuario}",tags=['Buscar usuário'],response_model=PessoaPublica)
def buscar_id_usuario(id_usuario:IdUsuario,
            session:SessionDP):
    get_usuario = session.get(Pessoa,id_usuario)
    if not get_usuario:
        raise HTTPException(status_code=404,detail='Usuário não encontrado')
    return get_usuario

@app.patch("/usuarios/{buscar_id}",response_model=PessoaPublica,tags=['Atualizar campos do usuário'])
def atualizar_user(buscar_id:IdUsuario,
             session:SessionDP,pessoa:PessoaAtualizar):
    buscar_usuario = session.get(Pessoa,buscar_id)
    if not buscar_usuario:
        raise HTTPException(status_code=404,detail="Usuário não encontrado")
    pessoa_db = pessoa.model_dump(exclude_unset=True)
    if "email" in pessoa_db:
        novo_email = pessoa.email
        if novo_email is not None and novo_email != buscar_usuario.email:
            statement = select(Pessoa).where(Pessoa.email == novo_email, Pessoa.id != buscar_usuario.id)
            pessoa_existente = session.exec(statement).first()
            if pessoa_existente:
                raise HTTPException(status_code=409,detail="Email em uso!")
    buscar_usuario.sqlmodel_update(pessoa_db)
    session.add(buscar_usuario)
    session.commit()
    session.refresh(buscar_usuario)
    return buscar_usuario

@app.delete("/usuarios/{buscar_id}",tags=['Remover usuário'],response_model=Msg)
def deletar_user(buscar_id:IdUsuario,session:SessionDP):
    buscar_usuario = session.get(Pessoa,buscar_id)
    if not buscar_usuario:
        raise HTTPException(status_code=404,detail='Usuário não encontrado')
    session.delete(buscar_usuario)
    session.commit()
    return Msg(mensagem="Usuário deletado com sucesso!")
    


    

    











