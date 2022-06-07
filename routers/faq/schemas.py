from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class FaqBase(BaseModel):
    title: str
    content: str
    flg: Optional[bool] = True

class Faq(FaqBase):
    id: int

    class Config:
        orm_mode = True