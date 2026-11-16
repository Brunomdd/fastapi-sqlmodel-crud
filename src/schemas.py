from pydantic import EmailStr, BaseModel,field_validator
from sqlmodel import SQLModel, Field
class PessoaBase(SQLModel):
    nome:str | None = Field(default=None,index=True,min_length=3,max_length=50)
    idade:int | None = Field(default=None,gt=18,le=120)
    
class Pessoa(PessoaBase,table=True):
    id:int | None = Field(default=None,primary_key=True)
    email:EmailStr| None = Field(default=None,unique=True)
    senha:str 
    
    
class CriarPessoa(PessoaBase):
    email:EmailStr
    senha:str 
    @field_validator('senha')
    @classmethod
    def validar_senha(cls,senha:str) -> str:
        if len(senha) <7:
            raise ValueError('A senha deve ter no mínimo 8 caracteres')
        if not any(c.islower() for c in senha):
            raise ValueError('A senha deve ter uma letra minuscula')
        if not any(c.isupper() for c in senha):
            raise ValueError('A senha deve ter uma letras maiuscula')
        if not any(c.digit() for c in senha):
            raise ValueError('A senha deve ter pelo menos um número')
    
        return senha 

        
    

class PessoaPublica(PessoaBase):
    id:int
    

class PessoaAtualizar(PessoaBase):
    nome:str | None = Field(default=None,min_length=3,max_length=50) 
    idade: int |None = Field(default=None,gt=18,le=120)
    email:EmailStr | None = None
    senha:str

class Msg(BaseModel):
    mensagem:str




    



