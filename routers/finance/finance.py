import os

from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session
from db.connection import get_db

from fastapi import APIRouter, Depends, Security, HTTPException, status
from fastapi.responses import JSONResponse

from ..auth.auth import get_current_user
from ..utils import finance_crud
from . import schemas


router = APIRouter(
    prefix="/finance",
    tags=["金融"],
    responses={404: {"descriptions": "Not found"}}
)


# 為替レートメインページDashBoard
@router.get("/main", response_model=List[schemas.ExchangeRate_DAT])
async def get_finance_dat(db: Session = Depends(get_db)):
    return finance_crud.get_finance_dat(db=db)

