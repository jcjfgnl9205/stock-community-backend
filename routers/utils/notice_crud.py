from sqlalchemy.orm import Session
from sqlalchemy import func, case
from .. import models
from ..notice import schemas
from datetime import datetime
from fastapi import status
from fastapi.responses import JSONResponse


# Notice Create
def create_notice(db: Session, notice: schemas.NoticeCreate, user_id: int):
    db_notice = models.Notice(**notice.dict(), user_id=user_id)
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return get_notice(db=db, notice_id=db_notice.id)


# Notice List
def get_notices(db: Session):
    return db.query(models.Notice.id
                    , models.Notice.title
                    , models.Notice.views
                    , models.Notice.created_at
                    , func.substring(models.User.email, 1, func.instr(models.User.email, '@') - 1).label("writer")
                    , func.count(models.NoticeComment.notice_id).label("notice_comment_cnt"))\
            .join(models.User, models.Notice.user_id == models.User.id)\
            .join(models.NoticeComment, models.Notice.id == models.NoticeComment.notice_id, isouter=True)\
            .filter(models.Notice.deleted_at == None)\
            .filter(models.NoticeComment.deleted_at == None)\
            .order_by(models.Notice.id.desc())\
            .group_by(models.Notice.id)\
            .all()


# Notice Detail
def get_notice(db: Session, notice_id: int):
    return db.query(models.Notice.id
                , models.Notice.title
                , models.Notice.content
                , models.Notice.views
                , func.sum(case([(models.NoticeVote.like == True, 1)], else_=0)).label("like_cnt")
                , func.sum(case([(models.NoticeVote.hate == True, 1)], else_=0)).label("hate_cnt")
                , models.Notice.created_at
                , models.Notice.updated_at
                , models.User.id.label("writer_id")
                , func.substring(models.User.email, 1, func.instr(models.User.email, '@') - 1).label("writer"))\
            .join(models.User, models.Notice.user_id == models.User.id)\
            .join(models.NoticeVote, models.Notice.id == models.NoticeVote.notice_id, isouter=True)\
        .filter(models.Notice.id == notice_id)\
        .filter(models.Notice.deleted_at == None)\
        .first()


# Notice Update
def update_notice(db: Session, notice_id: int, notice: schemas.NoticeUpdate):
    db_notice = db.query(models.Notice).filter(models.Notice.id == notice_id).first()
    db_notice.title = notice.title
    db_notice.content = notice.content
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return get_notice(db=db, notice_id=db_notice.id)


# Notice Delete
def delete_notice(db: Session, notice_id: int):
    db_notice = db.query(models.Notice).filter(models.Notice.id == notice_id).first()
    db_notice.deleted_at = get_datetime()
    db.add(db_notice)
    db.commit()
    db.refresh(db_notice)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "Success"})


# Notice Comment Create
def create_notice_comment(db: Session, comment: schemas.CommentCreate, notice_id: int, user_id: int):
    db_comment = models.NoticeComment(**comment.dict(), notice_id=notice_id, user_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return get_notice_comments(db=db, notice_id=notice_id)


# Notice Comment List
def get_notice_comments(db: Session, notice_id: int):
    return db.query(models.Notice.id
                , models.NoticeComment.id
                , models.NoticeComment.comment
                , models.NoticeComment.created_at
                , models.NoticeComment.updated_at
                , models.User.id.label("writer_id")
                , func.substring(models.User.email, 1, func.instr(models.User.email, '@') - 1).label("writer"))\
            .join(models.NoticeComment, models.Notice.id == models.NoticeComment.notice_id)\
            .join(models.User, models.NoticeComment.user_id == models.User.id)\
            .filter(models.Notice.id == notice_id)\
            .filter(models.NoticeComment.deleted_at == None)\
            .order_by(models.NoticeComment.id.desc())\
            .all()


# Notice Comment Detail
def get_notice_comment(db: Session, comment_id: int):
    return db.query(models.NoticeComment)\
            .filter(models.NoticeComment.id == comment_id)\
            .filter(models.NoticeComment.deleted_at == None)\
            .first()


# Notice Comment Update
def update_notice_comment(db: Session, comment_id: int, comment: schemas.CommentUpdate):
    db_comment = db.query(models.NoticeComment).filter(models.NoticeComment.id == comment_id).first()
    db_comment.comment = comment.comment
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return get_notice_comments(db=db, notice_id=db_comment.notice_id)


# Notice Comment Delete
def delete_notice_comment(db: Session, comment_id: int):
    db_comment = db.query(models.NoticeComment).filter(models.NoticeComment.id == comment_id).first()
    db_comment.deleted_at = get_datetime()
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return get_notice_comments(db=db, notice_id=db_comment.notice_id)


# Notice Get Like, Hate
def get_votes(db: Session, notice_id: int):
    return db.query(models.NoticeVote)\
            .filter(models.NoticeVote.notice_id == notice_id)\
            .all()


# Notice Set Like, Hate Update
def update_vote(db: Session, vote: schemas.VoteUpdate, notice_id: int, user_id: int):
    db_like = db.query(models.NoticeVote)\
                .filter(models.NoticeVote.notice_id == notice_id)\
                .filter(models.NoticeVote.user_id == user_id)\
                .first()

    if db_like:
        db_like.like = vote.like
        db_like.hate = vote.hate
        db.add(db_like)
        db.commit()
        db.refresh(db_like)
        return get_votes(db=db, notice_id=notice_id)

    db_like = models.NoticeVote(**vote.dict(), notice_id=notice_id, user_id=user_id)
    db.add(db_like)
    db.commit()
    db.refresh(db_like)
    return get_votes(db=db, notice_id=notice_id)


def get_datetime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
