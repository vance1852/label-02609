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


@router.post("", response_model=ResponseModel)
async def create_leave(
    data: LeaveCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    success, message, leave = LeaveService.create_leave(
        db, current_user.id, data.leave_type, data.start_date, data.end_date, data.reason
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return ResponseModel(message=message, data=LeaveService._to_dict(leave))


@router.get("/my", response_model=ResponseModel)
async def get_my_leaves(
    page: int = 1,
    page_size: int = 10,
    leave_status: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    leaves, total = LeaveService.get_my_leaves(
        db, current_user.id, status=leave_status, skip=skip, limit=page_size
    )
    return ResponseModel(data={"list": leaves, "total": total, "page": page, "page_size": page_size})


@router.get("/pending", response_model=ResponseModel)
async def get_pending_leaves(
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    leaves, total = LeaveService.get_pending_leaves(db, skip=skip, limit=page_size)
    return ResponseModel(data={"list": leaves, "total": total, "page": page, "page_size": page_size})


@router.get("/all", response_model=ResponseModel)
async def get_all_leaves(
    page: int = 1,
    page_size: int = 10,
    leave_status: Optional[str] = Query(None, alias="status"),
    user_id: Optional[int] = None,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    leaves, total = LeaveService.get_all_leaves(
        db, status=leave_status, user_id=user_id, skip=skip, limit=page_size
    )
    return ResponseModel(data={"list": leaves, "total": total, "page": page, "page_size": page_size})


@router.put("/{leave_id}/approve", response_model=ResponseModel)
async def approve_leave(
    leave_id: int,
    data: LeaveApprove,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    success, message, leave = LeaveService.approve_leave(
        db, leave_id, current_user.id, data.status, data.approval_comment
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return ResponseModel(message=message, data=LeaveService._to_dict(leave))


@router.get("/dates", response_model=ResponseModel)
async def get_leave_dates(
    user_id: int,
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dates = LeaveService.get_approved_leave_dates(db, user_id, start_date, end_date)
    return ResponseModel(data=[d.isoformat() for d in dates])
