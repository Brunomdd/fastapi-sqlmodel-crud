from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI,Depends,Query,HTTPException
from sqlmodel import Field,create_engine,Session,SQLModel,select
from pydantic import EmailStr,BaseModel

class PessoaBase(SQLModel):
    nome:str | None = Field(default=None,index=True)
    idade:int | None = Field(default=None)
    
    
class Pessoa(PessoaBase,table=True):
    id:int | None = Field(default=None,primary_key=True)
    email:EmailStr

class CriarPessoa(PessoaBase):
    email:EmailStr


class PessoaPublica(PessoaBase):
    id:int



class PessoaAtualizar(PessoaBase):
    nome:str | None = None
    idade: int | None = None
    email:EmailStr | None = None


class Msg(BaseModel):
    mensagem:str

sql_name = "banco.db"
sql_file_name = f"sqlite:///{sql_name}"
connect_args = {"check_same_thread":False}
engine = create_engine(sql_file_name,connect_args=connect_args)

def create_and_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@asynccontextmanager
async def lifespan(app:FastAPI):
    create_and_db()
    yield


app = FastAPI(lifespan=lifespan,title='API')

SessionDP = Annotated[Session,Depends(get_session)]


@app.post("/criar/",tags=['Criar usuário'],response_model=PessoaPublica)
def criar_usuario(pessoa:CriarPessoa,session:SessionDP):
    validar = Pessoa.model_validate(pessoa)
    session.add(validar)
    session.commit()
    session.refresh(validar)
    return validar

@app.get("/listar/usuarios",tags=['Listar Usuários'],response_model=list[PessoaPublica])
def listar_todos(session:SessionDP,offset:int=0,limit:Annotated[int,Query(le=100)] = 100):
    pessoas = session.exec(select(Pessoa).offset(offset).limit(limit)).all()
    return pessoas



@app.get("/buscar/usuario/{id_usuario}",tags=['Buscar usuário'],response_model=PessoaPublica)
def buscar_usuario(id_usuario:int,session:SessionDP):
    get_usuario = session.get(Pessoa,id_usuario)
    if not get_usuario:
        raise HTTPException(status_code=404,detail='Usuário não encontrado')
    return get_usuario

@app.patch("/Atualizar/{buscar_id}",response_model=PessoaPublica,tags=['Atualizar campos do usuário'])
def atualizar_user(buscar_id:int,session:SessionDP,pessoa:PessoaAtualizar):
    buscar_usuario = session.get(Pessoa,buscar_id)
    if not buscar_usuario:
        raise HTTPException(status_code=404,detail="Usuário não encontrado")
    pessoa_db = pessoa.model_dump(exclude_unset=True)
    buscar_usuario.sqlmodel_update(pessoa_db)
    session.add(buscar_usuario)
    session.commit()
    session.refresh(buscar_usuario)
    return buscar_usuario

@app.delete("/deletar/usuário/{id_usuario}",tags=['Remover usuário'],response_model=Msg)
def deletar_user(buscar_id:int,session:SessionDP):
    buscar_usuario = session.get(Pessoa,buscar_id)
    if not buscar_usuario:
        raise HTTPException(status_code=404,detail='Usuário não encontrado')
    session.delete(buscar_usuario)
    session.commit()
    return Msg(mensagem="Usuário deletado com sucesso!")



    

    











