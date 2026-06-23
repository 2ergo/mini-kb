from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


# 表模型 table=True 表示要创建数据库表
class KnowledgeBase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship不是用来定义数据库字段的
    # 它的作用不是创建新列，而是创建一种查询逻辑。
    #
    # 它告诉
    # SQLModel：“当用户访问
    # my_kb.documents
    # 时，请自动去
    # Document
    # 表里查找所有
    # knowledge_base_id
    # 等于
    # my_kb.id
    # 的记录。”
    documents: List["Document"] = Relationship(back_populates="knowledge_base")
    chat_messages: List["ChatMessage"] = Relationship(back_populates="knowledge_base")


# 操作的class，没有table=true
class KnowledgeBaseCreate(SQLModel):
    name: str = Field(min_length=1, max_length=50)   #必填
    description: str | None = Field(default=None, max_length=200)


class KnowledgeBaseUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=50) #非必填
    description: str | None = Field(default=None, max_length=200)


class DocumentCreate(SQLModel):
    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class ChatMessageCreate(SQLModel):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)



class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    kb_id: int = Field(foreign_key="knowledgebase.id")  #外键
    filename: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)  #不要写成 created_at: datetime = datetime.utcnow() 因为这样会在程序启动时只执行一次，后面所有数据可能都用同一个时间。

    knowledge_base: Optional[KnowledgeBase] = Relationship(back_populates="documents")


class ChatMessage(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    kb_id: int = Field(foreign_key="knowledgebase.id")
    question: str
    answer: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    knowledge_base: Optional[KnowledgeBase] = Relationship(back_populates="chat_messages")