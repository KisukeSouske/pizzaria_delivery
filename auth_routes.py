from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.get("/login")
async def login():
    """
    Login endpoint.
    Testing!!!
    """
    return {"message": "Login endpoint. This is where users can log in."}