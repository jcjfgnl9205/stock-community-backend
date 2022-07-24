from pydantic import BaseModel


class ExchangeRate_DAT(BaseModel):
    id: int
    currency_to: str
    currency_from: str
    inc_dec: str
    inc_dec_per: str
    price: float

    class Config:
        orm_mode = True
