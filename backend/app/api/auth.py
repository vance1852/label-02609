from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.user import UserLogin, UserResponse
from app.schemas.common import ResponseModel, TokenResponse
from app.services.user_service import UserService
from app.api.deps import get_current_user
from app.models.user import User
import logging

router = APIRouter(prefix="/auth", tags=["认证"])
logger = logging.getLogger(__name__)


@router.post("/login", response_model=ResponseModel)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录"""
    user = UserService.authenticate(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    logger.info(f"用户登录: {user.username}")
    
    return ResponseModel(
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "real_name": user.real_name,
                "role": user.role
            }
        }
    )


@router.post("/logout", response_model=ResponseModel)
async def logout(current_user: User = Depends(get_current_user)):
    """用户登出"""
    logger.info(f"用户登出: {current_user.username}")
    return ResponseModel(message="登出成功")


@router.get("/me", response_model=ResponseModel)
async def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    has_face = UserService.user_has_face(db, current_user.id)
    dept_name = current_user.department.name if current_user.department else None
    
    return ResponseModel(
        data={
            "id": current_user.id,
            "username": current_user.username,
            "real_name": current_user.real_name,
            "employee_no": current_user.employee_no,
            "department_id": current_user.department_id,
            "department_name": dept_name,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "has_face": has_face
        }
    )
