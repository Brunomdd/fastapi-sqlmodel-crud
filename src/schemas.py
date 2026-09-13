from pydantic import EmailStr, BaseModel
from sqlmodel import SQLModel, Field


class PessoaBase(SQLModel):
    nome:str | None = Field(default=None,index=True,min_length=3,max_length=50)
    idade:int | None = Field(default=None,gt=18,le=120)
    
    
class Pessoa(PessoaBase,table=True):
    id:int | None = Field(default=None,primary_key=True)
    email:EmailStr| None = Field(default=None,unique=True)
    

class CriarPessoa(PessoaBase):
    email:EmailStr
    

class PessoaPublica(PessoaBase):
    id:int

class PessoaAtualizar(PessoaBase):
    nome:str | None = Field(default=None,min_length=3,max_length=50) 
    idade: int |None = Field(default=None,gt=18,le=120)
    email:EmailStr | None = None

class Msg(BaseModel):
    mensagem:str