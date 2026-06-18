from fastapi import APIRouter

from services.notice_service import (
    get_all_notices,
    get_latest_notices,
    get_notices_by_category,
)

router = APIRouter(
    prefix="/notices",
    tags=["Notices"]
)


@router.get("/")
def all_notices():
    return get_all_notices()


@router.get("/latest")
def latest_notices():
    return get_latest_notices()


@router.get("/category/{category}")
def notices_by_category(category: str):
    return get_notices_by_category(category)