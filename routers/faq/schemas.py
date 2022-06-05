from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class FaqBase(BaseModel):
    title: str
    content: str

class Faq(FaqBase):
    id: int
    flg: bool

    class Config:
        orm_mode = True