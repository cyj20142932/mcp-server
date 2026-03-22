# FastAPI待办事项Demo实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现一个完整的FastAPI待办事项管理API Demo，包含CRUD操作、SQLite数据库集成和自动生成的Swagger文档。

**Architecture:** 使用FastAPI作为Web框架，SQLAlchemy作为ORM连接SQLite数据库，Pydantic进行数据验证。应用采用分层架构，将路由、业务逻辑和数据访问分离到不同的文件中。

**Tech Stack:** FastAPI, SQLAlchemy, SQLite, Pydantic, Uvicorn

---

## 文件结构

**创建新文件:**
- `requirements.txt` - Python依赖包
- `main.py` - FastAPI应用主文件
- `database.py` - 数据库连接和配置
- `models.py` - SQLAlchemy数据库模型
- `schemas.py` - Pydantic数据验证模型
- `crud.py` - 数据库CRUD操作函数
- `README.md` - 项目说明文档

**修改现有文件:** 无（从零开始）

**测试文件:**
- `test_main.py` - API端点测试

## 实施任务

### Task 1: 设置项目环境和依赖

**文件:**
- Create: `requirements.txt`

- [ ] **Step 1: 创建requirements.txt文件**

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
```

- [ ] **Step 2: 验证文件创建**

Run: `cat requirements.txt`
Expected: 显示依赖列表

- [ ] **Step 3: 提交**

```bash
git add requirements.txt
git commit -m "chore: 添加项目依赖"
```

### Task 2: 配置数据库连接

**文件:**
- Create: `database.py`

- [ ] **Step 1: 创建数据库连接文件**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./todo.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 2: 验证文件创建**

Run: `python -c "import database; print('Database module imported successfully')"`
Expected: "Database module imported successfully"

- [ ] **Step 3: 提交**

```bash
git add database.py
git commit -m "feat: 添加数据库连接配置"
```

### Task 3: 定义数据模型

**文件:**
- Create: `models.py`

- [ ] **Step 1: 创建数据库模型**

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

- [ ] **Step 2: 验证模型定义**

Run: `python -c "from models import Todo; print('Todo model imported successfully')"`
Expected: "Todo model imported successfully"

- [ ] **Step 3: 提交**

```bash
git add models.py
git commit -m "feat: 添加待办事项数据模型"
```

### Task 4: 定义Pydantic模式

**文件:**
- Create: `schemas.py`

- [ ] **Step 1: 创建Pydantic模式**

```python
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class Todo(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

- [ ] **Step 2: 验证模式定义**

Run: `python -c "from schemas import TodoCreate; print('Schemas imported successfully')"`
Expected: "Schemas imported successfully"

- [ ] **Step 3: 提交**

```bash
git add schemas.py
git commit -m "feat: 添加Pydantic数据验证模式"
```

### Task 5: 创建CRUD操作函数

**文件:**
- Create: `crud.py`

- [ ] **Step 1: 创建CRUD函数**

```python
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import models
import schemas

def get_todo(db: Session, todo_id: int):
    return db.query(models.Todo).filter(models.Todo.id == todo_id).first()

def get_todos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    completed: Optional[bool] = None
):
    query = db.query(models.Todo)

    if completed is not None:
        query = query.filter(models.Todo.completed == completed)

    return query.order_by(desc(models.Todo.created_at)).offset(skip).limit(limit).all()

def create_todo(db: Session, todo: schemas.TodoCreate):
    db_todo = models.Todo(
        title=todo.title,
        description=todo.description,
        completed=todo.completed
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_todo(db: Session, todo_id: int, todo: schemas.TodoUpdate):
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return None

    update_data = todo.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_todo, field, value)

    db.commit()
    db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, todo_id: int):
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return None

    db.delete(db_todo)
    db.commit()
    return db_todo
```

- [ ] **Step 2: 验证CRUD函数**

Run: `python -c "from crud import get_todos; print('CRUD functions imported successfully')"`
Expected: "CRUD functions imported successfully"

- [ ] **Step 3: 提交**

```bash
git add crud.py
git commit -m "feat: 添加数据库CRUD操作函数"
```

### Task 6: 创建数据库表和初始化数据

**文件:**
- Create: `init_db.py`

- [ ] **Step 1: 创建数据库初始化脚本**

创建 `init_db.py`:
```python
import models
from database import engine, SessionLocal

def init_db():
    """初始化数据库，创建表并添加示例数据"""
    # 创建所有表
    models.Base.metadata.create_all(bind=engine)

    # 添加示例数据
    db = SessionLocal()
    try:
        # 检查是否已有数据
        count = db.query(models.Todo).count()
        if count == 0:
            # 添加示例待办事项
            todos = [
                models.Todo(title="学习FastAPI", description="创建一个简单的FastAPI demo", completed=False),
                models.Todo(title="编写文档", description="为FastAPI demo编写README", completed=False),
                models.Todo(title="测试API", description="测试所有端点是否正常工作", completed=True),
            ]
            db.add_all(todos)
            db.commit()
            print("数据库已初始化并添加示例数据")
        else:
            print(f"数据库中已有 {count} 条记录")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    print("数据库初始化完成！")
```

- [ ] **Step 2: 运行初始化脚本**

Run: `python init_db.py`
Expected: "数据库已初始化并添加示例数据" 或 "数据库中已有 X 条记录"

- [ ] **Step 3: 提交**

```bash
git add init_db.py
git commit -m "feat: 添加数据库初始化功能"
```

### Task 7: 创建FastAPI主应用

**文件:**
- Create: `main.py`

- [ ] **Step 1: 创建FastAPI应用**

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import crud
import models
import schemas
from database import SessionLocal, engine, get_db

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="待办事项API",
    description="一个简单的FastAPI待办事项管理API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["根端点"])
async def root():
    return {
        "message": "欢迎使用待办事项API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            {"method": "GET", "path": "/todos", "description": "获取所有待办事项"},
            {"method": "GET", "path": "/todos/{id}", "description": "获取单个待办事项"},
            {"method": "POST", "path": "/todos", "description": "创建待办事项"},
            {"method": "PUT", "path": "/todos/{id}", "description": "更新待办事项"},
            {"method": "DELETE", "path": "/todos/{id}", "description": "删除待办事项"},
        ]
    }

@app.get("/todos", response_model=List[schemas.Todo], tags=["待办事项"])
async def read_todos(
    skip: int = 0,
    limit: int = 100,
    completed: bool = None,
    db: Session = Depends(get_db)
):
    """
    获取所有待办事项

    - **skip**: 跳过的记录数（用于分页）
    - **limit**: 返回的最大记录数（默认100）
    - **completed**: 筛选已完成或未完成的事项
    """
    todos = crud.get_todos(db, skip=skip, limit=limit, completed=completed)
    return todos

@app.get("/todos/{todo_id}", response_model=schemas.Todo, tags=["待办事项"])
async def read_todo(todo_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个待办事项

    - **todo_id**: 待办事项的ID
    """
    db_todo = crud.get_todo(db, todo_id=todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="待办事项未找到")
    return db_todo

@app.post("/todos", response_model=schemas.Todo, status_code=status.HTTP_201_CREATED, tags=["待办事项"])
async def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    """
    创建新的待办事项

    - **title**: 任务标题（必需）
    - **description**: 任务描述（可选）
    - **completed**: 是否已完成（默认False）
    """
    return crud.create_todo(db=db, todo=todo)

@app.put("/todos/{todo_id}", response_model=schemas.Todo, tags=["待办事项"])
async def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)):
    """
    更新待办事项

    - **todo_id**: 待办事项的ID
    - 可以更新标题、描述和完成状态
    """
    db_todo = crud.update_todo(db, todo_id=todo_id, todo=todo)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="待办事项未找到")
    return db_todo

@app.delete("/todos/{todo_id}", tags=["待办事项"])
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """
    删除待办事项

    - **todo_id**: 待办事项的ID
    """
    db_todo = crud.delete_todo(db, todo_id=todo_id)
    if db_todo is None:
        raise HTTPException(status_code=404, detail="待办事项未找到")
    return {"message": "待办事项已删除"}
```

- [ ] **Step 2: 验证应用导入**

Run: `python -c "import main; print('Main application imported successfully')"`
Expected: "Main application imported successfully"

- [ ] **Step 3: 提交**

```bash
git add main.py
git commit -m "feat: 添加FastAPI主应用和所有端点"
```

### Task 8: 创建测试文件

**文件:**
- Create: `test_main.py`

- [ ] **Step 1: 创建API测试**

```python
import pytest
from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_read_root():
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "欢迎使用待办事项API"
    assert "docs" in data
    assert "endpoints" in data

def test_create_todo():
    """测试创建待办事项"""
    todo_data = {
        "title": "测试任务",
        "description": "这是一个测试任务",
        "completed": False
    }
    response = client.post("/todos", json=todo_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "测试任务"
    assert data["description"] == "这是一个测试任务"
    assert data["completed"] == False
    assert "id" in data
    assert "created_at" in data
    return data["id"]  # 返回创建的待办事项ID供后续测试使用

def test_read_todos():
    """测试获取所有待办事项"""
    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "id" in data[0]
        assert "title" in data[0]

def test_read_todo():
    """测试获取单个待办事项"""
    # 先创建一个待办事项
    todo_data = {
        "title": "测试读取任务",
        "description": "测试获取单个任务",
        "completed": False
    }
    create_response = client.post("/todos", json=todo_data)
    todo_id = create_response.json()["id"]

    # 读取创建的待办事项
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "测试读取任务"

def test_update_todo():
    """测试更新待办事项"""
    # 先创建一个待办事项
    todo_data = {
        "title": "原始任务",
        "description": "原始描述",
        "completed": False
    }
    create_response = client.post("/todos", json=todo_data)
    todo_id = create_response.json()["id"]

    # 更新待办事项
    update_data = {
        "title": "更新后的任务",
        "completed": True
    }
    response = client.put(f"/todos/{todo_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "更新后的任务"
    assert data["completed"] == True

def test_delete_todo():
    """测试删除待办事项"""
    # 先创建一个待办事项
    todo_data = {
        "title": "待删除任务",
        "description": "这个任务将被删除",
        "completed": False
    }
    create_response = client.post("/todos", json=todo_data)
    todo_id = create_response.json()["id"]

    # 删除待办事项
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "待办事项已删除"

    # 验证已删除
    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 404

def test_read_nonexistent_todo():
    """测试获取不存在的待办事项"""
    response = client.get("/todos/99999")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "待办事项未找到"
```

- [ ] **Step 2: 运行测试验证失败**

Run: `pytest test_main.py -v`
Expected: 所有测试都通过或部分通过（取决于数据库状态）

- [ ] **Step 3: 提交**

```bash
git add test_main.py
git commit -m "test: 添加API端点测试"
```

### Task 9: 创建项目说明文档

**文件:**
- Create: `README.md`

- [ ] **Step 1: 创建README文件**

```markdown
# FastAPI待办事项API Demo

一个使用FastAPI构建的简单待办事项管理API Demo，包含完整的CRUD操作、SQLite数据库集成和自动生成的Swagger文档。

## 特性

- ✅ 完整的CRUD操作（创建、读取、更新、删除）
- ✅ SQLite数据库持久化
- ✅ 自动生成的Swagger API文档
- ✅ Pydantic数据验证
- ✅ SQLAlchemy ORM
- ✅ 单元测试
- ✅ CORS支持

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python init_db.py
```

### 3. 启动服务

```bash
uvicorn main:app --reload
```

### 4. 访问API

- API根端点: http://localhost:8000/
- Swagger文档: http://localhost:8000/docs
- ReDoc文档: http://localhost:8000/redoc

## API端点

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/` | 欢迎消息和API信息 |
| GET | `/todos` | 获取所有待办事项 |
| GET | `/todos/{id}` | 根据ID获取单个待办事项 |
| POST | `/todos` | 创建新的待办事项 |
| PUT | `/todos/{id}` | 更新待办事项 |
| DELETE | `/todos/{id}` | 删除待办事项 |

## 请求示例

### 创建待办事项
```bash
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "学习FastAPI",
    "description": "创建一个简单的API demo",
    "completed": false
  }'
```

### 获取所有待办事项
```bash
curl "http://localhost:8000/todos"
```

### 更新待办事项
```bash
curl -X PUT "http://localhost:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "更新后的任务",
    "completed": true
  }'
```

## 项目结构

```
.
├── main.py              # FastAPI应用主文件
├── requirements.txt     # Python依赖包
├── database.py         # 数据库连接配置
├── models.py           # SQLAlchemy数据库模型
├── schemas.py          # Pydantic数据验证模式
├── crud.py             # 数据库CRUD操作函数
├── init_db.py          # 数据库初始化脚本
├── test_main.py        # API测试
└── README.md           # 项目说明文档
```

## 运行测试

```bash
pytest test_main.py -v
```

## 技术栈

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的Web框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL工具包和ORM
- [SQLite](https://www.sqlite.org/) - 轻量级嵌入式数据库
- [Pydantic](https://docs.pydantic.dev/) - 数据验证和设置管理
- [Uvicorn](https://www.uvicorn.org/) - 快速的ASGI服务器

## 许可证

MIT
```

- [ ] **Step 2: 验证README文件**

Run: `cat README.md | head -10`
Expected: 显示README文件的前10行

- [ ] **Step 3: 提交**

```bash
git add README.md
git commit -m "docs: 添加项目说明文档"
```

### Task 10: 完整功能测试

**文件:**
- 所有已创建的文件

- [ ] **Step 1: 安装所有依赖**

Run: `pip install -r requirements.txt`
Expected: 所有依赖包安装成功

- [ ] **Step 2: 运行数据库初始化**

Run: `python init_db.py`
Expected: "数据库已初始化并添加示例数据" 或 "数据库中已有 X 条记录"

- [ ] **Step 3: 启动FastAPI应用（后台运行）**

Run: `uvicorn main:app --reload &`
Expected: 应用启动成功，显示 "Uvicorn running on http://127.0.0.1:8000"

- [ ] **Step 4: 测试API端点**

Run: `curl -s http://localhost:8000/ | python -m json.tool`
Expected: 返回欢迎消息和API信息

- [ ] **Step 5: 测试Swagger文档**

Run: `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs`
Expected: 返回200

- [ ] **Step 6: 停止应用**

Run: `pkill -f "uvicorn main:app"`
Expected: 应用停止运行

- [ ] **Step 7: 运行完整测试套件**

Run: `pytest test_main.py -v`
Expected: 所有测试通过

- [ ] **Step 8: 最终提交**

```bash
git add .
git commit -m "feat: FastAPI待办事项Demo完成

- 完整的CRUD API端点
- SQLite数据库集成
- 自动Swagger文档生成
- 完整的测试套件
- 项目说明文档

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

## 验证清单

- [ ] 所有文件创建完成
- [ ] 依赖安装成功
- [ ] 数据库初始化正常
- [ ] FastAPI应用启动成功
- [ ] API端点正常工作
- [ ] Swagger文档可访问
- [ ] 所有测试通过
- [ ] README文档完整

## 后续步骤

1. 可以选择使用superpowers:subagent-driven-development逐个任务执行
2. 或使用superpowers:executing-plans批量执行
3. 执行完成后，使用superpowers:verification-before-completion验证所有功能