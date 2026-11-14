from sqlmodel import SQLModel, create_engine, Session

sql_file_name = f"sqlite:///banco.db"
connect_args = {"check_same_thread":False}
engine = create_engine(sql_file_name,connect_args=connect_args)

def create_and_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()



