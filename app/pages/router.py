from uuid import UUID

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import EmailStr

from app.models.users import UserModel
from app.routers.dependencies import get_current_active_user

router = APIRouter(prefix="/pages", tags=["Frontend"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/confirm", response_class=HTMLResponse)
async def get_confirm_email_page(request: Request, id: UUID, email: EmailStr):
    return templates.TemplateResponse(
        "confirm_email.html", {"request": request, "id": id, "email": email}
    )


@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/profile", response_class=HTMLResponse)
async def get_profile_page(
    request: Request,
    user: UserModel = Depends(get_current_active_user),
):
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})
