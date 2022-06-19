from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, validator
from fastapi import File, UploadFile, Form


class STOCK_MST(BaseModel):
    id: Optional[int]
    name: str
    path: Optional[str]
    show_name: Optional[str]

class VoteBase(BaseModel):
    like: Optional[bool] = False
    hate: Optional[bool] = False

class Vote(VoteBase):
    user_id: int

    class Config:
        orm_mode = True

class VoteUpdate(VoteBase):
    pass


class StockBase(BaseModel):
    title: str
    content: str

class Stocks(BaseModel):
    id: int
    title: str
    views: int
    created_at: datetime
    stock_comment_cnt: Optional[int] = 0
    like_cnt: Optional[int] = 0
    writer: str

class Stock(StockBase):
    id: int 
    views: int
    like_cnt: int = 0
    hate_cnt: int = 0
    created_at: datetime
    updated_at: datetime
    stock_comment_cnt: int
    writer_id: int
    writer: str

    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    comment: str

class Comment(CommentBase):
    id: int
    writer_id: int
    writer: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
