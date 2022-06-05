from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct
from .. import models
from ..faq import schemas
from datetime import datetime


# Faq Create
def create_faq(db: Session, faq: schemas.FaqBase):
    db_faq = models.Faq(**faq.dict())
    db.add(db_faq)
    db.commit()
    db.refresh(db_faq)
    return get_faqs(db=db)


# Faq List
def get_faqs(db: Session):
    return db.query(models.Faq)\
                .filter(models.Faq.flg == True)\
                .filter(models.Faq.deleted_at == None)\
                .all()


# Faq Read
def get_faq(db: Session, faq_id: int):
    return db.query(models.Faq)\
                .filter(models.Faq.id == faq_id)\
                .filter(models.Faq.flg == True)\
                .filter(models.Faq.deleted_at == None)\
                .first()


# Faq Update
def update_faq(db:Session, faq: schemas.FaqBase, faq_id: int):
    db_faq = db.query(models.Faq).filter(models.Faq.id == faq_id).first()
    db_faq.title = faq.title
    db_faq.content = faq.content
    db.commit()
    db.refresh(db_faq)
    return get_faq(db=db, faq_id=faq_id)


# Faq Flg Update
def update_faq_flg(db: Session, faq: schemas.Faq, faq_id: int):
    db_faq = db.query(models.Faq).filter(models.Faq.id == faq_id).first()
    db_faq.flg = faq.flg
    db.commit()
    db.refresh(db_faq)
    return get_faq(db=db, faq_id=faq_id)


# Faq Delete
def delete_faq(db: Session, faq_id: int):
    db_faq = db.query(models.Faq).filter(models.Faq.id == faq_id).first()
    db_faq.deleted_at = get_datetime()
    db.commit()
    db.refresh(db_faq)
    return get_faqs(db=db)


def get_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
