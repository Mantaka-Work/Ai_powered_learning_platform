"""Authentication routes."""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

from app.db.supabase_client import get_supabase_client

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    role: str = "student"  # student or admin


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user."""
    try:
        supabase = get_supabase_client()
        
        # Create user with Supabase Auth
        response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "full_name": request.full_name,
                    "role": request.role
                }
            }
        })
        
        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed"
            )
        
        return AuthResponse(
            access_token=response.session.access_token if response.session else "",
            user={
                "id": str(response.user.id),
                "email": response.user.email,
                "role": request.role,
                "full_name": request.full_name
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login user."""
    try:
        supabase = get_supabase_client()
        
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        user_metadata = response.user.user_metadata or {}
        
        return AuthResponse(
            access_token=response.session.access_token,
            user={
                "id": str(response.user.id),
                "email": response.user.email,
                "role": user_metadata.get("role", "student"),
                "full_name": user_metadata.get("full_name", "")
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/logout")
async def logout():
    """Logout user."""
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
