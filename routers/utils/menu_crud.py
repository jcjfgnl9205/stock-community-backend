from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct
from .. import models
from ..stock import schemas
from datetime import datetime
from fastapi import status
from fastapi.responses import JSONResponse


def get_menus(db: Session):
    return db.query(models.MENU_MST)\
            .order_by(models.MENU_MST.show_order)\
            .all()


def get_sub_menu(db: Session, menu_id: int):
    return db.query(models.MENU_SUB_MST)\
            .filter(models.MENU_SUB_MST.menu_id == menu_id)\
            .order_by(models.MENU_SUB_MST.show_order)\
            .all()

