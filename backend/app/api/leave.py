from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.core.database import get_db
from app.schemas.common import ResponseModel
from app.schemas.leave import LeaveCreate, LeaveApprove
from app.services.leave_service import LeaveService
from app.api.deps import get_current_user, get_admin_user
from app.models.user import User
import logging

router = APIRouter(prefix="/leave", tags=["请假管理"])
logger = logging.getLogger(__name__)


@router.post("/apply", response_model=ResponseModel)
async def apply_leave(
    leave_data: LeaveCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交请假申请 - 员工使用"""
    success, message, leave = LeaveService.create_leave(db, current_user.id, leave_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return ResponseModel(message=message, data=LeaveService.format_leave_response(leave))


@router.get("/my", response_model=ResponseModel)
async def get_my_leaves(
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = Query(None, description="筛选状态: pending/approved/rejected"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的请假记录 - 员工使用"""
    skip = (page - 1) * page_size
    leaves = LeaveService.get_user_leaves(
        db, user_id=current_user.id, skip=skip, limit=page_size, status=status
    )
    total = LeaveService.get_user_leave_count(db, user_id=current_user.id, status=status)
    
    leave_list = [LeaveService.format_leave_response(leave) for leave in leaves]
    
    return ResponseModel(
        data={"list": leave_list, "total": total, "page": page, "page_size": page_size}
    )


@router.get("", response_model=ResponseModel)
async def get_all_leaves(
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = Query(None, description="筛选状态: pending/approved/rejected"),
    user_id: Optional[int] = Query(None, description="按用户ID筛选"),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取所有请假记录 - 管理员使用"""
    skip = (page - 1) * page_size
    leaves = LeaveService.get_all_leaves(
        db, skip=skip, limit=page_size, status=status, user_id=user_id
    )
    total = LeaveService.get_all_leave_count(db, status=status, user_id=user_id)
    
    leave_list = [LeaveService.format_leave_response(leave) for leave in leaves]
    
    return ResponseModel(
        data={"list": leave_list, "total": total, "page": page, "page_size": page_size}
    )


@router.get("/{leave_id}", response_model=ResponseModel)
async def get_leave_detail(
    leave_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取请假详情"""
    leave = LeaveService.get_leave_by_id(db, leave_id)
    
    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="请假申请不存在"
        )
    
    if current_user.role != "admin" and leave.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权查看该请假申请"
        )
    
    return ResponseModel(data=LeaveService.format_leave_response(leave))


@router.post("/{leave_id}/approve", response_model=ResponseModel)
async def approve_leave(
    leave_id: int,
    approve_data: LeaveApprove,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """通过请假申请 - 管理员使用"""
    success, message, leave = LeaveService.approve_leave(
        db, leave_id=leave_id, approver_id=current_user.id,
        approved=True, comment=approve_data.comment
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return ResponseModel(message=message, data=LeaveService.format_leave_response(leave))


@router.post("/{leave_id}/reject", response_model=ResponseModel)
async def reject_leave(
    leave_id: int,
    reject_data: LeaveApprove,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """驳回请假申请 - 管理员使用"""
    success, message, leave = LeaveService.approve_leave(
        db, leave_id=leave_id, approver_id=current_user.id,
        approved=False, comment=reject_data.comment
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return ResponseModel(message=message, data=LeaveService.format_leave_response(leave))
