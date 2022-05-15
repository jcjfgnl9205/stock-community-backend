from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, validator
from fastapi import File, UploadFile, Form


class Vote(BaseModel):
    like: Optional[bool] = False
    hate: Optional[bool] = False

    class Config:
        orm_mode = True

class VoteUpdate(Vote):
    pass


class NoticeBase(BaseModel):
    title: str
    content: str

class NoticeCreate(NoticeBase):
    pass

class NoticeUpdate(NoticeBase):
    writer_id: int

class Notices(BaseModel):
    id: int
    title: str
    views: int
    created_at: datetime
    notice_comment_cnt: Optional[int] = 0
    user_name: str

class Notice(NoticeBase):
    id: int 
    views: int
    like_cnt: int = 0
    hate_cnt: int = 0
    created_at: datetime
    updated_at: datetime
    writer_id: int
    user_name: str

    class Config:
        orm_mode = True


class CommentBase(BaseModel):
    comment: str

class Comment(CommentBase):
    id: int
    user_id: int
    user_name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CommentCreate(CommentBase):
    pass

class CommentUpdate(CommentBase):
    writer_id: int
