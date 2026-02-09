from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.department import DepartmentCreate, DepartmentUpdate
from app.schemas.common import ResponseModel
from app.services.department_service import DepartmentService
from app.api.deps import get_admin_user
from app.models.user import User
import logging

router = APIRouter(prefix="/departments", tags=["部门管理"])
logger = logging.getLogger(__name__)


@router.get("", response_model=ResponseModel)
async def get_departments(
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取部门列表"""
    skip = (page - 1) * page_size
    departments = DepartmentService.get_departments(db, skip=skip, limit=page_size)
    total = DepartmentService.get_department_count(db)
    
    dept_list = []
    for dept in departments:
        user_count = DepartmentService.get_user_count_by_department(db, dept.id)
        dept_list.append({
            "id": dept.id,
            "name": dept.name,
            "description": dept.description,
            "user_count": user_count,
            "created_at": dept.created_at.isoformat()
        })
    
    return ResponseModel(
        data={
            "list": dept_list,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    )


@router.get("/all", response_model=ResponseModel)
async def get_all_departments(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取所有部门（下拉选择用）"""
    departments = DepartmentService.get_departments(db, skip=0, limit=1000)
    dept_list = [{"id": d.id, "name": d.name} for d in departments]
    return ResponseModel(data=dept_list)


@router.post("", response_model=ResponseModel)
async def create_department(
    dept_data: DepartmentCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """创建部门"""
    existing = DepartmentService.get_department_by_name(db, dept_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="部门名称已存在"
        )
    
    dept = DepartmentService.create_department(db, dept_data)
    return ResponseModel(message="创建成功", data={"id": dept.id})


@router.put("/{dept_id}", response_model=ResponseModel)
async def update_department(
    dept_id: int,
    dept_data: DepartmentUpdate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """更新部门"""
    # 检查名称是否重复
    if dept_data.name:
        existing = DepartmentService.get_department_by_name(db, dept_data.name)
        if existing and existing.id != dept_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="部门名称已存在"
            )
    
    dept = DepartmentService.update_department(db, dept_id, dept_data)
    if not dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="部门不存在"
        )
    return ResponseModel(message="更新成功")


@router.delete("/{dept_id}", response_model=ResponseModel)
async def delete_department(
    dept_id: int,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """删除部门"""
    try:
        success = DepartmentService.delete_department(db, dept_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="部门不存在"
            )
        return ResponseModel(message="删除成功")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
