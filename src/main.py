from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI,Depends
from sqlmodel import Field,create_engine,Session,SQLModel

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


@app.get("/testando")
def teste():
    return {"teste rota"}










