from fastapi import APIRouter

from app.routers.private import (
    users as private_users,
    auth as private_auth,
)
from app.routers.public import (
    auth as public_auth,
    users as public_users,
)


router_public = APIRouter()
router_public.include_router(
    public_auth.router, tags=["Public auth routers"], prefix="/auth"
)
router_public.include_router(
    public_users.router, tags=["Public users routers"], prefix="/users"
)

router_private = APIRouter()
router_private.include_router(
    private_users.router, tags=["Private users routers"], prefix="/users"
)
router_private.include_router(
    private_auth.router, tags=["Private auth routers"], prefix="/auth"
)
