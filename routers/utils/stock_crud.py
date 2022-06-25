from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct
from .. import models
from ..stock import schemas
from datetime import datetime
from fastapi import status
from fastapi.responses import JSONResponse


def get_stocks_mst(db: Session):
    return db.query(models.STOCK_MST).all()


# Category Check
def get_stock_mst(db: Session, stock: str):
    return db.query(models.STOCK_MST).filter(models.STOCK_MST.name == stock).first()


# Stock List
def get_stocks(db: Session, stock_id: int):
    vote_sub_query = db.query(models.STOCK_DETAIL_DAT.id
                            , func.sum(case([(models.STOCK_DETAIL_VOTE_DAT.like == True, 1)], else_=0)).label("like_cnt")
                            , func.sum(case([(models.STOCK_DETAIL_VOTE_DAT.hate == True, 1)], else_=0)).label("hate_cnt"))\
            .join(models.STOCK_DETAIL_VOTE_DAT, models.STOCK_DETAIL_DAT.id == models.STOCK_DETAIL_VOTE_DAT.stock_id, isouter=True)\
            .group_by(models.STOCK_DETAIL_DAT.id)\
            .filter(models.STOCK_DETAIL_DAT.deleted_at == None)\
            .subquery('vote_sub_query')

    comment_sub_query = db.query(models.STOCK_DETAIL_DAT.id
                                , func.count(models.STOCK_DETAIL_COMMENT_DAT.id).label("notice_comment_cnt"))\
            .join(models.STOCK_DETAIL_COMMENT_DAT, models.STOCK_DETAIL_DAT.id == models.STOCK_DETAIL_COMMENT_DAT.stock_id, isouter=True)\
            .group_by(models.STOCK_DETAIL_DAT.id)\
            .filter(models.STOCK_DETAIL_DAT.deleted_at == None)\
            .subquery('comment_sub_query')

    return db.query(models.STOCK_DETAIL_DAT.id
                    , models.STOCK_DETAIL_DAT.title
                    , models.STOCK_DETAIL_DAT.views
                    , models.STOCK_DETAIL_DAT.created_at
                    , func.substring(models.USER.email, 1, func.instr(models.USER.email, '@') - 1).label("writer")
                    , vote_sub_query.c.like_cnt
                    , comment_sub_query.c.notice_comment_cnt)\
            .join(models.USER, models.STOCK_DETAIL_DAT.user_id == models.USER.id)\
            .join(vote_sub_query, models.STOCK_DETAIL_DAT.id == vote_sub_query.c.id)\
            .join(comment_sub_query, models.STOCK_DETAIL_DAT.id == comment_sub_query.c.id)\
            .join(models.STOCK_MST, models.STOCK_DETAIL_DAT.stock_mst_id == models.STOCK_MST.id)\
            .filter(models.STOCK_MST.id == stock_id)\
            .filter(models.STOCK_DETAIL_DAT.deleted_at == None)\
            .order_by(models.STOCK_DETAIL_DAT.id.desc())\
            .group_by(models.STOCK_DETAIL_DAT.id)\
            .all()

# Stock Detail
def get_stock(db: Session, stock_id: int):
    vote_sub_query = db.query(models.STOCK_DETAIL_DAT.id
                , func.sum(case([(models.STOCK_DETAIL_VOTE_DAT.like == True, 1)], else_=0)).label("like_cnt")
                , func.sum(case([(models.STOCK_DETAIL_VOTE_DAT.hate == True, 1)], else_=0)).label("hate_cnt"))\
            .join(models.STOCK_DETAIL_VOTE_DAT, models.STOCK_DETAIL_DAT.id == models.STOCK_DETAIL_VOTE_DAT.stock_id, isouter=True)\
            .group_by(models.STOCK_DETAIL_DAT.id)\
            .filter(models.STOCK_DETAIL_DAT.id == stock_id)\
            .filter(models.STOCK_DETAIL_DAT.deleted_at == None)\
            .subquery('vote_sub_query')

    comment_sub_query = db.query(models.STOCK_DETAIL_DAT.id
                                , func.count(models.STOCK_DETAIL_COMMENT_DAT.id).label("notice_comment_cnt"))\
            .join(models.STOCK_DETAIL_COMMENT_DAT, models.STOCK_DETAIL_DAT.id == models.STOCK_DETAIL_COMMENT_DAT.stock_id, isouter=True)\
            .group_by(models.STOCK_DETAIL_DAT.id)\
            .filter(models.STOCK_DETAIL_DAT.deleted_at == None)\
            .filter(models.STOCK_DETAIL_COMMENT_DAT.deleted_at == None)\
            .subquery('comment_sub_query')

    return db.query(models.STOCK_DETAIL_DAT.id
                , models.STOCK_DETAIL_DAT.title
                , models.STOCK_DETAIL_DAT.content
                , models.STOCK_DETAIL_DAT.views
                , models.STOCK_DETAIL_DAT.created_at
                , models.STOCK_DETAIL_DAT.updated_at
                , vote_sub_query.c.like_cnt
                , vote_sub_query.c.hate_cnt
                , models.USER.id.label("writer_id")
                , comment_sub_query.c.notice_comment_cnt
                , func.substring(models.USER.email, 1, func.instr(models.USER.email, '@') - 1).label("writer"))\
            .join(models.USER, models.STOCK_DETAIL_DAT.user_id == models.USER.id)\
            .join(comment_sub_query, models.STOCK_DETAIL_DAT.id == comment_sub_query.c.id)\
            .join(vote_sub_query, models.STOCK_DETAIL_DAT.id == vote_sub_query.c.id)\
            .filter(models.STOCK_DETAIL_DAT.id == stock_id)\
            .first()

# Stock Create
def create_stock(db: Session, stock: schemas.StockBase, user_id: int, stock_mst_id: int):
    db_stock = models.STOCK_DETAIL_DAT(**stock.dict(), user_id=user_id, stock_mst_id=stock_mst_id)
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return get_stock(db=db, stock_id=db_stock.id)


# Stock View Count Update
def update_stock_view_count(db: Session, stock_id: int):
    db_stock = db.query(models.STOCK_DETAIL_DAT).filter(models.STOCK_DETAIL_DAT.id == stock_id).first()
    db_stock.views = db_stock.views + 1
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return get_stock(db=db, stock_id=db_stock.id)

# Stock Update
def update_stock(db: Session, stock_id: int, stock: schemas.StockBase):
    db_stock = db.query(models.STOCK_DETAIL_DAT).filter(models.STOCK_DETAIL_DAT.id == stock_id).first()
    db_stock.title = stock.title
    db_stock.content = stock.content
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return get_stock(db=db, stock_id=db_stock.id)


# Stock Delete
def delete_stock(db: Session, stock_id: int):
    db_stock = db.query(models.STOCK_DETAIL_DAT).filter(models.STOCK_DETAIL_DAT.id == stock_id).first()
    db_stock.deleted_at = get_datetime()
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Success"})


# Stock Comment Create
def create_stock_comment(db: Session, comment: schemas.CommentBase, stock_id: int, user_id: int):
    db_comment = models.STOCK_DETAIL_COMMENT_DAT(**comment.dict(), stock_id=stock_id, user_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return get_stock_comments(db=db, stock_id=stock_id)


# Stock Comment List
def get_stock_comments(db: Session, stock_id: int):
    return db.query(models.STOCK_DETAIL_DAT.id
                , models.STOCK_DETAIL_COMMENT_DAT.id
                , models.STOCK_DETAIL_COMMENT_DAT.comment
                , models.STOCK_DETAIL_COMMENT_DAT.created_at
                , models.STOCK_DETAIL_COMMENT_DAT.updated_at
                , models.USER.id.label("writer_id")
                , func.substring(models.USER.email, 1, func.instr(models.USER.email, '@') - 1).label("writer"))\
            .join(models.STOCK_DETAIL_COMMENT_DAT, models.STOCK_DETAIL_DAT.id == models.STOCK_DETAIL_COMMENT_DAT.stock_id)\
            .join(models.USER, models.STOCK_DETAIL_COMMENT_DAT.user_id == models.USER.id)\
            .filter(models.STOCK_DETAIL_DAT.id == stock_id)\
            .filter(models.STOCK_DETAIL_COMMENT_DAT.deleted_at == None)\
            .order_by(models.STOCK_DETAIL_COMMENT_DAT.id.desc())\
            .all()


# Stock Comment Detail
def get_stock_comment(db: Session, comment_id: int):
    return db.query(models.STOCK_DETAIL_COMMENT_DAT)\
            .filter(models.STOCK_DETAIL_COMMENT_DAT.id == comment_id)\
            .filter(models.STOCK_DETAIL_COMMENT_DAT.deleted_at == None)\
            .first()


# Stock Comment Update
def update_stock_comment(db: Session, comment_id: int, comment: schemas.CommentBase):
    db_comment = db.query(models.STOCK_DETAIL_COMMENT_DAT).filter(models.STOCK_DETAIL_COMMENT_DAT.id == comment_id).first()
    db_comment.comment = comment.comment
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return get_stock_comments(db=db, stock_id=db_comment.stock_id)


# Stock Comment Delete
def delete_stock_comment(db: Session, comment_id: int):
    db_comment = db.query(models.STOCK_DETAIL_COMMENT_DAT).filter(models.STOCK_DETAIL_COMMENT_DAT.id == comment_id).first()
    db_comment.deleted_at = get_datetime()
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return get_stock_comments(db=db, stock_id=db_comment.stock_id)


# Stock Get Like, Hate
def get_votes(db: Session, stock_id: int):
    return db.query(models.STOCK_DETAIL_VOTE_DAT)\
            .filter(models.STOCK_DETAIL_VOTE_DAT.stock_id == stock_id)\
            .all()


# Stock Set Like, Hate Update
def update_vote(db: Session, vote: schemas.VoteUpdate, stock_id: int, user_id: int):
    db_like = db.query(models.STOCK_DETAIL_VOTE_DAT)\
                .filter(models.STOCK_DETAIL_VOTE_DAT.stock_id == stock_id)\
                .filter(models.STOCK_DETAIL_VOTE_DAT.user_id == user_id)\
                .first()

    if db_like:
        db_like.like = vote.like
        db_like.hate = vote.hate
        db.add(db_like)
        db.commit()
        db.refresh(db_like)
        return get_votes(db=db, stock_id=stock_id)

    db_like = models.STOCK_DETAIL_VOTE_DAT(**vote.dict(), stock_id=stock_id, user_id=user_id)
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return get_votes(db=db, stock_id=stock_id)


def get_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
