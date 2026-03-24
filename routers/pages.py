from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/")
def index():
    return RedirectResponse(url="/static/index.html")


@router.get("/host")
def host():
    return RedirectResponse(url="/static/host.html")


@router.get("/guest")
def guest():
    return RedirectResponse(url="/static/guest.html")


@router.get("/admin")
def admin():
    return RedirectResponse(url="/static/admin.html")
