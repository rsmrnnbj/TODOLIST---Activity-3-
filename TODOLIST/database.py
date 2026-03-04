from sqlmodel import SQLModel, create_engine, Session

# Change "database.db" to "tasks.db"
sqlite_url = "sqlite:///tasks.db" 
engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session