from pydantic import BaseModel
from datetime import datetime


class ExchangeRate_DAT(BaseModel):
    id: int
    currency_to: str
    currency_from: str
    inc_dec: str
    inc_dec_per: str
    price: float
    created_at: datetime

    class Config:
        orm_mode = True
