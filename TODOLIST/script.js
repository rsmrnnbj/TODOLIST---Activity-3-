const API_BASE = "http://127.0.0.1:8000";
const API_URL = `${API_BASE}/tasks`;

// 1. Load tasks from the Database when the page opens
document.addEventListener('DOMContentLoaded', async () => {
    const userId = localStorage.getItem('userId');
    if (!userId) {
        window.location.href = 'index.html'; 
        return;
    }
    // Fetch only THIS user's tasks
    const response = await fetch(`${API_URL}/${userId}`);
    const tasks = await response.json();
    tasks.forEach(task => renderTask(task));
});

// 2. Add a new task to the Database
async function createNewTask() {
    const input = document.getElementById('taskInput');
    const taskValue = input.value.trim();
    const userId = localStorage.getItem('userId'); 

    if (taskValue === "") return;

    const vibes = ["✨ ", "🔥 ", "💀 ", "🤡 ", "🚀 "];
    const randomVibe = vibes[Math.floor(Math.random() * vibes.length)];
    const fullText = randomVibe + taskValue;

    const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            text: fullText, 
            user_id: parseInt(userId), 
            status: 'todo' 
        })
    });

    if (response.ok) {
        const newTask = await response.json();
        renderTask(newTask);
        input.value = "";
    }
}

// 3. Helper to display the task on the UI
function renderTask(task) {
    const taskCard = document.createElement('div');
    taskCard.className = 'task-card';
    taskCard.innerText = task.text;
    taskCard.id = `task-${task.id}`; 
    
    if (task.status === 'done') {
        taskCard.style.background = "#90ee90";
    }

    taskCard.onclick = () => moveTask(taskCard, task.id);

    const columnId = task.status === 'todo' ? 'todo-list' : 
                     task.status === 'progress' ? 'progress-list' : 'done-list';
    document.getElementById(columnId).appendChild(taskCard);
}

// 4. Update or BANISH from Database
async function moveTask(taskElement, id) {
    const parentId = taskElement.parentElement.id;
    let newStatus = "";

    if (parentId === 'todo-list') {
        newStatus = 'progress';
        document.getElementById('progress-list').appendChild(taskElement);
    } else if (parentId === 'progress-list') {
        newStatus = 'done';
        document.getElementById('done-list').appendChild(taskElement);
        if (!taskElement.innerText.includes("(W)")) {
            taskElement.innerText += " (W)";
        }
        taskElement.style.background = "#90ee90";
    } else {
        // BANISHMENT LOGIC: Send to Shadow Realm instead of simple delete
        const res = await fetch(`${API_BASE}/tasks/${id}/banish`, { method: 'POST' });
        if (res.ok) {
            alert("Task Sent to the Shadow Realm. It is now eternal in the DB. 💀");
            taskElement.remove();
        }
        return;
    }

    // PUT request to update status for To-Do and Progress moves
    await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
    });
}