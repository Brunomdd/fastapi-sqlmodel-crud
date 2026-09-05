from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI,Depends
from sqlmodel import Field,create_engine,Session,SQLModel
from pydantic import EmailStr

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


@app.post("/criar/",tags=['Criando usuário'],response_model=PessoaPublica)
def criar_usuario(pessoa:CriarPessoa,session:SessionDP):
    validar = Pessoa.model_validate(pessoa)
    session.add(validar)
    session.commit()
    session.refresh(validar)
    return validar










