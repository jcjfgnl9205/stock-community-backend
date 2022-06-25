import os
from typing import Optional, List

from sqlalchemy.orm import Session
from db.connection import get_db

from fastapi import APIRouter, Depends, Security, HTTPException, status, Body

from ..utils import menu_crud
from . import schemas


router = APIRouter(
    prefix="/menu",
    tags=["メニュー"],
    responses={404: {"descriptions": "Not found"}}
)

@router.get("", response_model=List[schemas.MenuMST])
async def get_menus(db: Session = Depends(get_db)):
    menu_mst = list()
    for v in menu_crud.get_menus(db=db):
        menu_mst.append(
            schemas.MenuMST(
                name=v.name
                , name_sub=v.name_sub
                , path=v.path
                , show_order=v.show_order
                , sub=menu_crud.get_sub_menu(db=db, menu_id=v.id)
            )
        )

    return menu_mst
