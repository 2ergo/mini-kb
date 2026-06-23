from contextlib import asynccontextmanager   #装饰器用法，替代旧用法 startup
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from database import create_db_and_tables, get_session
from models import KnowledgeBase, Document, ChatMessage, KnowledgeBaseCreate,KnowledgeBaseCreate,DocumentCreate,ChatMessageCreate

from typing import Optional, List



# 项目启动核心代码 FastAPI() 创建应后端应用实例
app = FastAPI(
    # 这几个参数主要是影响Swagger 文档
    title="Knowledge Base API",
    description="阶段 1：FastAPI 入门版接口，用内存数组模拟知识库项目",
    version="0.1.0",
)







# 创建路由
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "FastAPI service is running"
    }



@asynccontextmanager  # 把lifespan封装一下
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


# 创建知识库
@app.post("/knowledge-bases", response_model=KnowledgeBase)
def create_knowledge_base(
        kb: KnowledgeBaseCreate,
        session: Session = Depends(get_session)
):
    db_kb = KnowledgeBase.model_validate(kb)
    session.add(db_kb)
    session.commit()
    session.refresh(db_kb)
    return db_kb

# 查询全部知识库
@app.get("/knowledge-bases", response_model=List[KnowledgeBase])
def get_knowledge_bases(
        session: Session = Depends(get_session)
):
    statement = select(KnowledgeBase)
    return session.exec(statement).all()


# 查询单个数据库
@app.get("/knowledge-bases/{kb_id}", response_model=KnowledgeBase)
def get_knowledge_base(
        kb_id: int,
        session: Session = Depends(get_session)
):
    kb = session.get(KnowledgeBase, kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KnowledgeBase not found",
        )
    return kb

# 删除知识库
@app.delete("/knowledge-bases/{kb_id}")
def delete_knowledge_base(
        kb_id: int,
        session: Session = Depends(get_session)
):
    kb=session.get(KnowledgeBase, kb_id)
    if not kb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KnowledgeBase not found",
        )
    session.delete(kb)
    session.commit()
    return {"message": "KnowledgeBase deleted successfully"}


# Document API
# 新增文档
@app.post("/knowledge-bases/{kb_id}/documents", response_model=Document)
def create_document(
        kb_id: int,
        doc: Document,
        session: Session = Depends(get_session)
):
    kb = session.get(KnowledgeBase, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="KnowledgeBase not found")
    doc.kb_id = kb_id
    session.add(doc)
    session.commit()
    session.refresh(doc)
    return doc

# 查询某个知识库下的文档
@app.get("/knowledge-bases/{kb_id}/documents", response_model=List[Document])
def get_document(
        kb_id: int,
        session: Session = Depends(get_session)
):
    kb=session.get(KnowledgeBase, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="KnowledgeBase not found")
    # session.get()是按主键查询一条
    statement = session.exec(select(Document).where(Document.id == kb_id)).all()
    return statement

# Chat message API
# 新增问答记录
@app.post("/knowledge-bases/{kb_id}/messages", response_model=ChatMessage)
def create_chat_message(
        kb_id: int,
        message: ChatMessage,
        session: Session = Depends(get_session)
):
    kb = session.get(KnowledgeBase, kb_id)
    if not kb:
        raise HTTPException(status_code=404, detail="KnowledgeBase not found")
    message.kb_id = kb_id
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


# 查询某个知识库下的聊天记录
@app.get("/knowledge-bases/{kb_id}/messages", response_model=ChatMessage)
def get_chat_message(
        kb_id: int,
        session: Session = Depends(get_session)
):
    statement = select(ChatMessage).where(KnowledgeBase, kb_id)
    return session.exec(statement).all()
