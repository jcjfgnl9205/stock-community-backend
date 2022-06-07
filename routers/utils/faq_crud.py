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
                .filter(models.Faq.deleted_at == None)\
                .order_by(models.Faq.id.desc())\
                .all()


# Faq Read
def get_faq(db: Session, faq_id: int):
    return db.query(models.Faq)\
                .filter(models.Faq.id == faq_id)\
                .filter(models.Faq.deleted_at == None)\
                .first()


# Faq Update
def update_faq(db:Session, faq: schemas.FaqBase, faq_id: int):
    db_faq = db.query(models.Faq).filter(models.Faq.id == faq_id).first()
    db_faq.title = faq.title
    db_faq.content = faq.content
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
