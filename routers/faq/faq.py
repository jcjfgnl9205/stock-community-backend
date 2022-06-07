import os
from typing import List
from datetime import datetime

from sqlalchemy.orm import Session
from db.connection import get_db

from fastapi import APIRouter, Depends, HTTPException

from ..auth.auth import get_current_user
from ..utils import faq_crud
from . import schemas


router = APIRouter(
    prefix="/faq",
    tags=["FAQ"],
    responses={404: {"descriptions": "Not found"}}
)


@router.get("", response_model=List[schemas.Faq])
async def get_faqs(db: Session = Depends(get_db)):
    """
    <h2>QnAを全て表示する</h2>
    """
    return faq_crud.get_faqs(db=db)

@router.post("", response_model=List[schemas.Faq])
async def create_faq(faq: schemas.FaqBase, db: Session = Depends(get_db)):
    """
    <h2>QnAを登録する</h2>
    """
    return faq_crud.create_faq(db=db, faq=faq)

@router.put("/{faq_id}", response_model=schemas.Faq)
async def update_faq(faq_id: int, faq: schemas.Faq, db: Session = Depends(get_db)):
    """
    <h2>QnAを更新する</h2>
    """
    return faq_crud.update_faq(db=db, faq=faq, faq_id=faq_id)

@router.delete("/{faq_id}", response_model=List[schemas.Faq])
async def delete_faq(faq_id: int, db: Session = Depends(get_db)):
    """
    <h2>QnAを削除する</h2>
    """
    return faq_crud.delete_faq(db=db, faq_id=faq_id)
