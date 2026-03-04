import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, StaticPool
from main import app, get_session

# Ghost Database for testing
sqlite_url = "sqlite:///:memory:"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False}, poolclass=StaticPool)

def get_session_override():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = get_session_override
client = TestClient(app)

# 1. Test Setup (Creates the ghost tables)
def test_setup():
    SQLModel.metadata.create_all(engine)

# 2. Test Signup
def test_signup():
    response = client.post("/signup", json={"email": "meme@test.com", "password": "123"})
    assert response.status_code == 201

# 3. Test Login
def test_login():
    response = client.post("/login", json={"email": "meme@test.com", "password": "123"})
    assert response.status_code == 200

# 4. Test Create Task
def test_create_task():
    response = client.post("/tasks", json={"text": "Study Cloud", "user_id": 1, "status": "todo"})
    assert response.status_code == 200

# 5. Test Get Tasks
def test_get_tasks():
    response = client.get("/tasks/1")
    assert response.status_code == 200
    assert len(response.json()) > 0