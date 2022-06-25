from typing import List, Optional
from pydantic import BaseModel


class MenuSubMST(BaseModel):
    name: str
    name_sub: str
    path: str
    show_order: str

    class Config:
        orm_mode = True

class MenuMST(BaseModel):
    name: str
    name_sub: str
    path: str
    show_order: str
    sub: Optional[List[MenuSubMST]]

    class Config:
        orm_mode = True
