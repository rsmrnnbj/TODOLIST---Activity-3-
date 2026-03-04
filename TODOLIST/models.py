from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    password: str

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    text: str
    status: str = Field(default="todo")


class ShadowTask(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    user_id: int