from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import ResponseModel
from app.services.user_service import UserService
from app.services.face_service import FaceService
from app.api.deps import get_current_user, get_admin_user
from app.models.user import User
import logging

router = APIRouter(prefix="/users", tags=["用户管理"])
logger = logging.getLogger(__name__)


@router.get("", response_model=ResponseModel)
async def get_users(
    page: int = 1,
    page_size: int = 10,
    keyword: str = None,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    skip = (page - 1) * page_size
    users = UserService.get_users(db, skip=skip, limit=page_size, keyword=keyword)
    total = UserService.get_user_count(db, keyword=keyword)
    
    user_list = []
    for user in users:
        has_face = UserService.user_has_face(db, user.id)
        dept_name = user.department.name if user.department else None
        user_list.append({
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "employee_no": user.employee_no,
            "department_id": user.department_id,
            "department_name": dept_name,
            "role": user.role,
            "is_active": user.is_active,
            "has_face": has_face,
            "created_at": user.created_at.isoformat()
        })
    
    return ResponseModel(
        data={
            "list": user_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.post("", response_model=ResponseModel)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """创建用户"""
    # 检查用户名是否已存在
    existing = UserService.get_user_by_username(db, user_data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    user = UserService.create_user(db, user_data)
    return ResponseModel(message="创建成功", data={"id": user.id})


@router.put("/{user_id}", response_model=ResponseModel)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """更新用户"""
    user = UserService.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return ResponseModel(message="更新成功")


@router.delete("/{user_id}", response_model=ResponseModel)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """删除用户"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return ResponseModel(message="删除成功")


@router.post("/{user_id}/face", response_model=ResponseModel)
async def upload_face(
    user_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """上传人脸照片"""
    # 检查用户是否存在
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查文件类型
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请上传图片文件"
        )
    
    # 读取文件内容
    image_data = await file.read()
    
    # 注册人脸
    success, message = FaceService.register_face(db, user_id, image_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return ResponseModel(message=message)
