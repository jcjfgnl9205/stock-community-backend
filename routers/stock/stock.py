import os
from enum import Enum
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional, List

from sqlalchemy.orm import Session
from db.connection import get_db

from fastapi import APIRouter, Depends, Security, HTTPException, status, Body
from fastapi_pagination import Page, paginate, add_pagination
from fastapi.responses import JSONResponse

from ..auth.auth import get_current_user
from ..utils import stock_crud
from . import schemas


router = APIRouter(
    prefix="/stock",
    tags=["株掲示板"],
    responses={404: {"descriptions": "Not found"}}
)


def checked_category_mst(stock: str, db: Session = Depends(get_db)):
    isStock = stock_crud.get_stock_mst(db=db, stock=stock)
    if isStock is None:
        raise HTTPException(status_code=404, detail="stock not found")
    return isStock



@router.get("", response_model=List[schemas.STOCK_MST])
async def get_stocks_mst(db: Session = Depends(get_db)):
    return stock_crud.get_stocks_mst(db=db)


@router.post("/{stock}", response_model=schemas.Stock)
async def create_stock(stock_create: schemas.StockBase
                        , stock: schemas.STOCK_MST = Depends(checked_category_mst)
                        , current_user: str = Depends(get_current_user)
                        , db: Session = Depends(get_db)):
    return stock_crud.create_stock(db=db, stock=stock_create, user_id=current_user['user_id'], stock_mst_id=stock.id)



@router.get("/{stock}", response_model=Page[schemas.Stocks])
async def get_stocks(stock: schemas.STOCK_MST = Depends(checked_category_mst)
                    , paginationPage: Optional[int] = 0
                    , db: Session = Depends(get_db)):
    return paginate(stock_crud.get_stocks(db=db, stock_id=stock.id))



@router.get("/{stock}/{stock_id}", response_model=schemas.Stock)
async def get_stock(stock_id: int
                    , stock: schemas.STOCK_MST = Depends(checked_category_mst)
                    , db: Session = Depends(get_db)):
    stock = stock_crud.get_stock(db=db, stock_id=stock_id)
    if stock is None:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock



@router.put("/{stock}/{stock_id}/view-count")
def update_stock_view_count(stock_id: int
                            , stock: schemas.Stock = Depends(get_stock)
                            , db: Session = Depends(get_db)):
    return stock_crud.update_stock_view_count(db=db, stock_id=stock_id)



def get_stock_me(stock_id: int
                , stock: schemas.Stock = Depends(get_stock)
                , current_user: str = Depends(get_current_user)
                , db: Session = Depends(get_db)):
    if stock.writer_id != current_user['user_id']:
        raise HTTPException(status_code=401, detail="The writer and the login user are different")
    return stock



@router.put("/{stock}/{stock_id}", response_model=schemas.Stock)
async def update_stock(stock_id: int
                        , stock_update: schemas.StockBase
                        , current_user: str = Depends(get_current_user)
                        , stock: schemas.Stock = Depends(get_stock_me)
                        , db: Session = Depends(get_db)):
    return stock_crud.update_stock(db=db, stock_id=stock_id, stock=stock_update)



@router.delete("/{stock}/{stock_id}")
async def delete_stock(stock_id: int
                        , current_user: str = Depends(get_current_user)
                        , stock: schemas.Stock = Depends(get_stock_me)
                        , db: Session = Depends(get_db)):
    return stock_crud.delete_stock(db=db, stock_id=stock_id)



@router.post("/{stock}/{stock_id}/comment", response_model=Page[schemas.Comment])
async def create_stock_comment(stock_id: int
                                , comment: schemas.CommentBase
                                , stock: schemas.Stock = Depends(get_stock)
                                , current_user: str = Depends(get_current_user)
                                , db: Session = Depends(get_db)):
    return paginate(stock_crud.create_stock_comment(db=db, comment=comment, stock_id=stock_id, user_id=current_user['user_id']))



@router.get("/{stock}/{stock_id}/comments", response_model=Page[schemas.Comment])
async def get_stock_comments(stock_id: int
                            , stock: schemas.Stock = Depends(get_stock)
                            , db: Session = Depends(get_db)):
    return paginate(stock_crud.get_stock_comments(db=db, stock_id=stock_id))



async def get_stock_comment_me(stock_id: int
                            , comment_id: int
                            , stock: schemas.Stock = Depends(get_stock)
                            , current_user: str = Depends(get_current_user)
                            , db: Session = Depends(get_db)):
    comment = stock_crud.get_stock_comment(db=db, comment_id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Stock comment not found")
    if comment.user_id != current_user['user_id']:
        raise HTTPException(status_code=401, detail="The writer and the login user are different")
    return comment



@router.put("/{stock}/{stock_id}/comment/{comment_id}", response_model=Page[schemas.Comment])
async def update_stock_comment(stock_id: int
                                , comment_id: int
                                , comment: schemas.CommentBase
                                , stock_comment: schemas.Comment = Depends(get_stock_comment_me)
                                , current_user: str = Depends(get_current_user)
                                , db: Session = Depends(get_db)):
    return paginate(stock_crud.update_stock_comment(db=db, comment_id=comment_id, comment=comment))



@router.delete("/{stock}/{stock_id}/comment/{comment_id}", response_model=Page[schemas.Comment])
async def delete_stock_comment(stock_id: int
                                , comment_id: int
                                , stock_comment: schemas.Comment = Depends(get_stock_comment_me)
                                , current_user: str = Depends(get_current_user)
                                , db: Session = Depends(get_db)):
    return paginate(stock_crud.delete_stock_comment(db=db, comment_id=comment_id))



@router.get("/{stock}/{stock_id}/vote", response_model=List[schemas.Vote])
async def get_votes(stock_id: int
                    , stock: schemas.Stock = Depends(get_stock)
                    , db: Session = Depends(get_db)):
    return stock_crud.get_votes(db=db, stock_id=stock_id)



@router.post("/{stock}/{stock_id}/vote", response_model=List[schemas.Vote])
async def update_vote(stock_id: int
                        , vote: schemas.VoteUpdate
                        , stock: schemas.Stock = Depends(get_stock)
                        , current_user: str = Depends(get_current_user)
                        , db: Session = Depends(get_db)):
    return stock_crud.update_vote(db=db, vote=vote, stock_id=stock_id, user_id=current_user['user_id'])



add_pagination(router)
