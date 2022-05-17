import os
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional, List

from sqlalchemy.orm import Session
from db.connection import get_db

from fastapi import APIRouter, Depends, Security, HTTPException, status, Body
from fastapi_pagination import Page, paginate, add_pagination
from fastapi.responses import JSONResponse

from ..auth.auth import get_current_user
from ..utils import notice_crud
from . import schemas


router = APIRouter(
    prefix="/notices",
    tags=["掲示板"],
    responses={404: {"descriptions": "Not found"}}
)


@router.post("", response_model=schemas.Notice)
async def create_notice(notice: schemas.NoticeCreate
                        , current_user: str = Depends(get_current_user)
                        , db: Session = Depends(get_db)):
    """
    <h2>掲示板投稿</h2>
    掲示板に投稿する（Loginしているユーザーのみ投稿可能）
    """
    return notice_crud.create_notice(db=db, notice=notice, user_id=current_user['user_id'])


@router.get("", response_model=Page[schemas.Notices])
async def get_notices(paginationPage: Optional[int] = 0, db: Session = Depends(get_db)):
    """
    <h2>掲示板リスト</h2>
    掲示板のリストを取得する
    """
    return paginate(notice_crud.get_notices(db=db))


@router.get("/{notice_id}", response_model=schemas.Notice)
async def get_notice(notice_id: int, db: Session = Depends(get_db)):
    """
    <h2>掲示板詳細</h2>
    掲示板番号の詳細データを取得する
    
    ※ Raises
        HTTPException<br/>
        　　404: 掲示板番号が存在しない場合
    """
    notice = notice_crud.get_notice(db=db, notice_id=notice_id)
    if notice.id is None:
        raise HTTPException(status_code=404, detail="Notice not found")
    return notice


@router.put("/{notice_id}", response_model=schemas.Notice)
async def update_notice(notice_id: int
                        , notice: schemas.NoticeUpdate
                        , current_user: str = Depends(get_current_user)
                        , db: Session = Depends(get_db)):
    """
    <h2>掲示板更新</h2>
    掲示板番号の投稿内容を更新する
    
    ※ Raises
        HTTPException<br/>
        　　404: 掲示板番号が存在しない場合<br/>
        　　401: Loginしていない場合<br/>
        　　401: Loginしているユーザーと掲示板投稿者と異なっている場合<br/>
    """
    if notice.writer_id != current_user['user_id']:
        raise HTTPException(status_code=401, detail="The writer and the login user are different")
    return notice_crud.update_notice(db=db, notice_id=notice_id, notice=notice)


@router.delete("/{notice_id}")
async def delete_notice(notice_id: int
                        , notice: schemas.NoticeDelete
                        , current_user: str = Depends(get_current_user)
                        , db: Session = Depends(get_db)):
    """
    <h2>掲示板削除</h2>
    掲示板番号の投稿内容を削除する
    
    ※ Raises
        HTTPException<br/>
        　　404: 掲示板番号が存在しない場合<br/>
        　　401: Loginしていない場合<br/>
        　　401: Loginしているユーザーと掲示板投稿者と異なっている場合<br/>
    """
    if notice.writer_id != current_user['user_id']:
        raise HTTPException(status_code=401, detail="The writer and the login user are different")
    return notice_crud.delete_notice(db=db, notice_id=notice_id)


@router.post("/{notice_id}/comment", response_model=Page[schemas.Comment])
async def create_notice_comment(notice_id: int
                                , comment: schemas.CommentCreate
                                , get_notice: schemas.Notice = Depends(get_notice)
                                , current_user: str = Depends(get_current_user)
                                , db: Session = Depends(get_db)):
    """
    <h2>掲示板のコメント投稿</h2>
    掲示板の掲示板のコメントを投稿する
    
    ※ Raises
        HTTPException<br/>
        　　404: 掲示板番号番号が存在しない場合<br/>
        　　401: Loginしていない場合<br/>
    """
    return paginate(notice_crud.create_notice_comment(db=db, comment=comment, notice_id=notice_id, user_id=current_user['user_id']))


@router.get("/{notice_id}/comments", response_model=Page[schemas.Comment])
async def get_notice_comments(notice_id: int
                            , get_notice: schemas.Notice = Depends(get_notice)
                            , db: Session = Depends(get_db)):
    """
    <h2>掲示板のコメントリスト</h2>
    掲示板番号のコメントリストを取得する
    
    ※ Raises
        HTTPException<br/>
        　　404: 掲示板番号が存在しない場合<br/>
    """
    return paginate(notice_crud.get_notice_comments(db=db, notice_id=notice_id))


@router.get("/{notice_id}/comment/{comment_id}", response_model=schemas.Comment)
async def get_notice_comment(notice_id: int
                            , comment_id: int
                            , get_notice: schemas.Notice = Depends(get_notice)
                            , db: Session = Depends(get_db)):
    """
    <h2>掲示板のコメント詳細</h2>
    掲示板番号のコメント詳細情報を取得する
    
    ※ Raises
        HTTPException<br/>
        　　404: 掲示板番号、コメント番号が存在しない場合<br/>
    """
    comment = notice_crud.get_notice_comment(db=db, comment_id=comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Notice comment not found")
    return comment


@router.put("/{notice_id}/comment/{comment_id}", response_model=Page[schemas.Comment])
async def update_notice_comment(notice_id: int
                                , comment_id: int
                                , comment: schemas.CommentUpdate
                                , get_notice: schemas.Notice = Depends(get_notice)
                                , get_notice_comment: schemas.Comment = Depends(get_notice_comment)
                                , current_user: str = Depends(get_current_user)
                                , db: Session = Depends(get_db)):
    """
    <h2>掲示板のコメント更新</h2>
    掲示板の掲示板のコメントを更新する
    
    ※ Raises
        HTTPException<br/>
        　　404: 掲示板番号、コメント番号が存在しない場合<br/>
        　　401: Loginしていない場合<br/>
        　　401: Loginしているユーザーとコメント投稿者と異なっている場合<br/>
    """
    if comment.writer_id != current_user['user_id']:
        raise HTTPException(status_code=401, detail="The writer and the login user are different")
    return paginate(notice_crud.update_notice_comment(db=db, comment_id=comment_id, comment=comment))


@router.delete("/{notice_id}/comment/{comment_id}", response_model=Page[schemas.Comment])
async def delete_notice_comment(notice_id: int
                                , comment_id: int
                                , writer_id: int
                                , get_notice: schemas.Notice = Depends(get_notice)
                                , get_notice_comment: schemas.Comment = Depends(get_notice_comment)
                                , current_user: str = Depends(get_current_user)
                                , db: Session = Depends(get_db)):
    """
    <h2>掲示板のコメント削除</h2>
    掲示板の掲示板のコメントを削除する
    
    ※ Raises
        HTTPException<br/>
        　　404: 掲示板番号、コメント番号が存在しない場合<br/>
        　　401: Loginしていない場合<br/>
        　　401: Loginしているユーザーとコメント投稿者と異なっている場合<br/>
    """
    if writer_id != current_user['user_id']:
        raise HTTPException(status_code=401, detail="The writer and the login user are different")
    return paginate(notice_crud.delete_notice_comment(db=db, comment_id=comment_id))


@router.get("/{notice_id}/vote", response_model=List[schemas.Vote])
async def get_votes(notice_id: int
                    , get_notice: schemas.Notice = Depends(get_notice)
                    , db: Session = Depends(get_db)):
    """
    <h2>掲示板のLike, Hate count</h2>
    掲示板の掲示板のいいね、悪いボタンのカウント
    
    ※ Raises
        HTTPException<br/>
        　　404: 掲示板番号が存在しない場合<br/>
    """
    return notice_crud.get_votes(db=db, notice_id=notice_id)


@router.post("/{notice_id}/vote", response_model=List[schemas.Vote])
async def update_vote(notice_id: int
                        , vote: schemas.VoteUpdate
                        , get_notice: schemas.Notice = Depends(get_notice)
                        , current_user: str = Depends(get_current_user)
                        , db: Session = Depends(get_db)):
    """
    <h2>掲示板のLike, Hateボタンクリックイベント</h2>
    掲示板の掲示板のいいね、悪いボタンをクリックする
    
    ※ Raises
        HTTPException<br/>
        　　404: 掲示板番号が存在しない場合<br/>
        　　401: Loginしていない場合<br/>
    """
    return notice_crud.update_vote(db=db, vote=vote, notice_id=notice_id, user_id=current_user['user_id'])


add_pagination(router)
