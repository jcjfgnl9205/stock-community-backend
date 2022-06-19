from sqlalchemy.orm import Session
from sqlalchemy import func, case, distinct
from .. import models
from ..notice import schemas
from datetime import datetime
from fastapi import status
from fastapi.responses import JSONResponse


# Notice Create
def create_notice(db: Session, notice: schemas.NoticeBase, user_id: int):
    db_notice = models.NOTICE_DETAIL_DAT(**notice.dict(), user_id=user_id)
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return get_notice(db=db, notice_id=db_notice.id)


# Notice List
def get_notices(db: Session):
    vote_sub_query = db.query(models.NOTICE_DETAIL_DAT.id
                            , func.sum(case([(models.NOTICE_DETAIL_VOTE_DAT.like == True, 1)], else_=0)).label("like_cnt")
                            , func.sum(case([(models.NOTICE_DETAIL_VOTE_DAT.hate == True, 1)], else_=0)).label("hate_cnt"))\
            .join(models.NOTICE_DETAIL_VOTE_DAT, models.NOTICE_DETAIL_DAT.id == models.NOTICE_DETAIL_VOTE_DAT.notice_id, isouter=True)\
            .group_by(models.NOTICE_DETAIL_DAT.id)\
            .filter(models.NOTICE_DETAIL_DAT.deleted_at == None)\
            .subquery('vote_sub_query')

    comment_sub_query = db.query(models.NOTICE_DETAIL_DAT.id
                                , func.count(models.NOTICE_DETAIL_COMMENT_DAT.id).label("notice_comment_cnt"))\
            .join(models.NOTICE_DETAIL_COMMENT_DAT, models.NOTICE_DETAIL_DAT.id == models.NOTICE_DETAIL_COMMENT_DAT.notice_id, isouter=True)\
            .group_by(models.NOTICE_DETAIL_DAT.id)\
            .filter(models.NOTICE_DETAIL_DAT.deleted_at == None)\
            .subquery('comment_sub_query')

    return db.query(models.NOTICE_DETAIL_DAT.id
                    , models.NOTICE_DETAIL_DAT.title
                    , models.NOTICE_DETAIL_DAT.views
                    , models.NOTICE_DETAIL_DAT.created_at
                    , func.substring(models.USER.email, 1, func.instr(models.USER.email, '@') - 1).label("writer")
                    , vote_sub_query.c.like_cnt
                    , comment_sub_query.c.notice_comment_cnt)\
            .join(models.USER, models.NOTICE_DETAIL_DAT.user_id == models.USER.id)\
            .join(vote_sub_query, models.NOTICE_DETAIL_DAT.id == vote_sub_query.c.id)\
            .join(comment_sub_query, models.NOTICE_DETAIL_DAT.id == comment_sub_query.c.id)\
            .filter(models.NOTICE_DETAIL_DAT.deleted_at == None)\
            .order_by(models.NOTICE_DETAIL_DAT.id.desc())\
            .group_by(models.NOTICE_DETAIL_DAT.id)\
            .all()


# Notice Detail
def get_notice(db: Session, notice_id: int):
    vote_sub_query = db.query(models.NOTICE_DETAIL_DAT.id
                , func.sum(case([(models.NOTICE_DETAIL_VOTE_DAT.like == True, 1)], else_=0)).label("like_cnt")
                , func.sum(case([(models.NOTICE_DETAIL_VOTE_DAT.hate == True, 1)], else_=0)).label("hate_cnt"))\
            .join(models.NOTICE_DETAIL_VOTE_DAT, models.NOTICE_DETAIL_DAT.id == models.NOTICE_DETAIL_VOTE_DAT.notice_id, isouter=True)\
            .group_by(models.NOTICE_DETAIL_DAT.id)\
            .filter(models.NOTICE_DETAIL_DAT.id == notice_id)\
            .filter(models.NOTICE_DETAIL_DAT.deleted_at == None)\
            .subquery('vote_sub_query')

    comment_sub_query = db.query(models.NOTICE_DETAIL_DAT.id
                                , func.count(models.NOTICE_DETAIL_COMMENT_DAT.id).label("notice_comment_cnt"))\
            .join(models.NOTICE_DETAIL_COMMENT_DAT, models.NOTICE_DETAIL_DAT.id == models.NOTICE_DETAIL_COMMENT_DAT.notice_id, isouter=True)\
            .group_by(models.NOTICE_DETAIL_DAT.id)\
            .filter(models.NOTICE_DETAIL_DAT.deleted_at == None)\
            .filter(models.NOTICE_DETAIL_COMMENT_DAT.deleted_at == None)\
            .subquery('comment_sub_query')

    return db.query(models.NOTICE_DETAIL_DAT.id
                , models.NOTICE_DETAIL_DAT.title
                , models.NOTICE_DETAIL_DAT.content
                , models.NOTICE_DETAIL_DAT.views
                , models.NOTICE_DETAIL_DAT.created_at
                , models.NOTICE_DETAIL_DAT.updated_at
                , vote_sub_query.c.like_cnt
                , vote_sub_query.c.hate_cnt
                , models.USER.id.label("writer_id")
                , comment_sub_query.c.notice_comment_cnt
                , func.substring(models.USER.email, 1, func.instr(models.USER.email, '@') - 1).label("writer"))\
            .join(models.USER, models.NOTICE_DETAIL_DAT.user_id == models.USER.id)\
            .join(comment_sub_query, models.NOTICE_DETAIL_DAT.id == comment_sub_query.c.id)\
            .join(vote_sub_query, models.NOTICE_DETAIL_DAT.id == vote_sub_query.c.id)\
            .filter(models.NOTICE_DETAIL_DAT.id == notice_id)\
            .first()


# Notice View Count Update
def update_notice_view_count(db: Session, notice_id: int):
    db_notice = db.query(models.NOTICE_DETAIL_DAT).filter(models.NOTICE_DETAIL_DAT.id == notice_id).first()
    db_notice.views = db_notice.views + 1
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return get_notice(db=db, notice_id=db_notice.id)


# Notice Update
def update_notice(db: Session, notice_id: int, notice: schemas.NoticeBase):
    db_notice = db.query(models.NOTICE_DETAIL_DAT).filter(models.NOTICE_DETAIL_DAT.id == notice_id).first()
    db_notice.title = notice.title
    db_notice.content = notice.content
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return get_notice(db=db, notice_id=db_notice.id)


# Notice Delete
def delete_notice(db: Session, notice_id: int):
    db_notice = db.query(models.NOTICE_DETAIL_DAT).filter(models.NOTICE_DETAIL_DAT.id == notice_id).first()
    db_notice.deleted_at = get_datetime()
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Success"})


# Notice Comment Create
def create_notice_comment(db: Session, comment: schemas.CommentBase, notice_id: int, user_id: int):
    db_comment = models.NOTICE_DETAIL_COMMENT_DAT(**comment.dict(), notice_id=notice_id, user_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return get_notice_comments(db=db, notice_id=notice_id)


# Notice Comment List
def get_notice_comments(db: Session, notice_id: int):
    return db.query(models.NOTICE_DETAIL_DAT.id
                , models.NOTICE_DETAIL_COMMENT_DAT.id
                , models.NOTICE_DETAIL_COMMENT_DAT.comment
                , models.NOTICE_DETAIL_COMMENT_DAT.created_at
                , models.NOTICE_DETAIL_COMMENT_DAT.updated_at
                , models.USER.id.label("writer_id")
                , func.substring(models.USER.email, 1, func.instr(models.USER.email, '@') - 1).label("writer"))\
            .join(models.NOTICE_DETAIL_COMMENT_DAT, models.NOTICE_DETAIL_DAT.id == models.NOTICE_DETAIL_COMMENT_DAT.notice_id)\
            .join(models.USER, models.NOTICE_DETAIL_COMMENT_DAT.user_id == models.USER.id)\
            .filter(models.NOTICE_DETAIL_DAT.id == notice_id)\
            .filter(models.NOTICE_DETAIL_COMMENT_DAT.deleted_at == None)\
            .order_by(models.NOTICE_DETAIL_COMMENT_DAT.id.desc())\
            .all()


# Notice Comment Detail
def get_notice_comment(db: Session, comment_id: int):
    return db.query(models.NOTICE_DETAIL_COMMENT_DAT)\
            .filter(models.NOTICE_DETAIL_COMMENT_DAT.id == comment_id)\
            .filter(models.NOTICE_DETAIL_COMMENT_DAT.deleted_at == None)\
            .first()


# Notice Comment Update
def update_notice_comment(db: Session, comment_id: int, comment: schemas.CommentBase):
    db_comment = db.query(models.NOTICE_DETAIL_COMMENT_DAT).filter(models.NOTICE_DETAIL_COMMENT_DAT.id == comment_id).first()
    db_comment.comment = comment.comment
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return get_notice_comments(db=db, notice_id=db_comment.notice_id)


# Notice Comment Delete
def delete_notice_comment(db: Session, comment_id: int):
    db_comment = db.query(models.NOTICE_DETAIL_COMMENT_DAT).filter(models.NOTICE_DETAIL_COMMENT_DAT.id == comment_id).first()
    db_comment.deleted_at = get_datetime()
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return get_notice_comments(db=db, notice_id=db_comment.notice_id)


# Notice Get Like, Hate
def get_votes(db: Session, notice_id: int):
    return db.query(models.NOTICE_DETAIL_VOTE_DAT)\
            .filter(models.NOTICE_DETAIL_VOTE_DAT.notice_id == notice_id)\
            .all()


# Notice Set Like, Hate Update
def update_vote(db: Session, vote: schemas.VoteUpdate, notice_id: int, user_id: int):
    db_like = db.query(models.NOTICE_DETAIL_VOTE_DAT)\
                .filter(models.NOTICE_DETAIL_VOTE_DAT.notice_id == notice_id)\
                .filter(models.NOTICE_DETAIL_VOTE_DAT.user_id == user_id)\
                .first()

    if db_like:
        db_like.like = vote.like
        db_like.hate = vote.hate
        db.add(db_like)
        db.commit()
        db.refresh(db_like)
        return get_votes(db=db, notice_id=notice_id)

    db_like = models.NOTICE_DETAIL_VOTE_DAT(**vote.dict(), notice_id=notice_id, user_id=user_id)
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return get_votes(db=db, notice_id=notice_id)


def get_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
