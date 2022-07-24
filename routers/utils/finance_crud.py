from sqlalchemy.orm import Session, aliased
from sqlalchemy import func, case, distinct
from .. import models
from ..stock import schemas

from fastapi import status


def get_finance_dat(db: Session):
    currency_mst_a = aliased(models.CURRENCY_MST)
    currency_mst_b = aliased(models.CURRENCY_MST)

    sub_query = db.query(models.CURRENCY_DAT.currency_to
                        , models.CURRENCY_DAT.currency_from
                        , func.max(models.CURRENCY_DAT.id).label("id"))\
                .group_by(models.CURRENCY_DAT.currency_to
                        , models.CURRENCY_DAT.currency_from)\
                .subquery('sub_query')


    return db.query(models.CURRENCY_DAT.id
                    , currency_mst_a.currency.label("currency_to")
                    , currency_mst_b.currency.label("currency_from")
                    , models.CURRENCY_DAT.inc_dec
                    , models.CURRENCY_DAT.inc_dec_per
                    , models.CURRENCY_DAT.price)\
                .join(currency_mst_a, models.CURRENCY_DAT.currency_to == currency_mst_a.id)\
                .join(currency_mst_b, models.CURRENCY_DAT.currency_from == currency_mst_b.id)\
                .join(sub_query, models.CURRENCY_DAT.id == sub_query.c.id)\
                .all()
