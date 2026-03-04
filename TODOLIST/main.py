from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from typing import List
from database import engine, create_db_and_tables, get_session
from models import User, Task, ShadowTask

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user_data: User, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    session.add(user_data)
    session.commit()
    session.refresh(user_data)
    return {"message": "User Created", "user_id": user_data.id}

@app.post("/login")
def login(user_data: User, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == user_data.email, User.password == user_data.password)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"message": "Success", "user_id": user.id}

@app.get("/tasks/{user_id}", response_model=List[Task])
def get_tasks(user_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Task).where(Task.user_id == user_id)).all()

@app.post("/tasks", response_model=Task)
def add_task(task: Task, session: Session = Depends(get_session)):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# UPDATE task status (This handles the (W) persistence logic)
@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_update: Task, session: Session = Depends(get_session)):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    db_task.status = task_update.status
    
    # Logic: Add (W) if moved to 'done' and not already there
    if db_task.status == 'done' and "(W)" not in db_task.text:
        db_task.text += " (W)"
    
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return {"message": "Task updated", "text": db_task.text}

# DELETE task (Shadow Realm)
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session)):
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    session.delete(db_task)
    session.commit()
    return {"message": "Banishment complete"}

@app.post("/tasks/{task_id}/banish")
def banish_task(task_id: int, session: Session = Depends(get_session)):
    # 1. Find the task in the living world
    db_task = session.get(Task, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 2. Create a copy in the Shadow Realm table
    shadow_record = ShadowTask(text=db_task.text, user_id=db_task.user_id)
    session.add(shadow_record)
    
    # 3. Delete it from the active tasks
    session.delete(db_task)
    
    session.commit()
    return {"message": "Task Sent to the Shadow Realm.", "shadow_id": shadow_record.id}