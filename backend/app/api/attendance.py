from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from app.core.database import get_db
from app.schemas.common import ResponseModel
from app.services.attendance_service import AttendanceService
from app.api.deps import get_current_user, get_admin_user
from app.models.user import User
import logging

router = APIRouter(prefix="/attendance", tags=["考勤管理"])
logger = logging.getLogger(__name__)


@router.post("/check-in", response_model=ResponseModel)
async def check_in(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """人脸签到 - 需要登录，验证人脸是否匹配当前用户"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请上传图片文件"
        )
    
    if not current_user.face_encodings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您尚未录入人脸信息，请先在员工管理中录入人脸"
        )
    
    image_data = await file.read()
    success, message, data = AttendanceService.check_in_with_user(db, image_data, current_user)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    
    return ResponseModel(message=message, data=data)


@router.post("/check-out", response_model=ResponseModel)
async def check_out(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """人脸签退 - 需要登录，验证人脸是否匹配当前用户"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请上传图片文件"
        )
    
    if not current_user.face_encodings:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您尚未录入人脸信息，请先在员工管理中录入人脸"
        )
    
    image_data = await file.read()
    success, message, data = AttendanceService.check_out_with_user(db, image_data, current_user)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    
    return ResponseModel(message=message, data=data)


@router.post("/public/check-in", response_model=ResponseModel)
async def public_check_in(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """公开人脸签到 - 无需登录，通过人脸识别身份"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请上传图片文件")
    
    image_data = await file.read()
    success, message, data = AttendanceService.check_in(db, image_data)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    
    return ResponseModel(message=message, data=data)


@router.post("/public/check-out", response_model=ResponseModel)
async def public_check_out(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """公开人脸签退 - 无需登录，通过人脸识别身份"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请上传图片文件")
    
    image_data = await file.read()
    success, message, data = AttendanceService.check_out(db, image_data)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    
    return ResponseModel(message=message, data=data)


@router.get("", response_model=ResponseModel)
async def get_attendances(
    page: int = 1,
    page_size: int = 10,
    user_id: Optional[int] = None,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取考勤记录"""
    skip = (page - 1) * page_size
    records = AttendanceService.get_attendances(
        db, user_id=user_id, start_date=start_date, end_date=end_date,
        skip=skip, limit=page_size
    )
    total = AttendanceService.get_attendance_count(
        db, user_id=user_id, start_date=start_date, end_date=end_date
    )
    
    record_list = []
    for record in records:
        user = record.user
        dept_name = user.department.name if user.department else None
        record_list.append({
            "id": record.id,
            "user_id": record.user_id,
            "user_name": user.real_name,
            "employee_no": user.employee_no,
            "department_name": dept_name,
            "attendance_date": record.attendance_date.isoformat(),
            "record_type": record.record_type,
            "record_type_text": "签到" if record.record_type == "check_in" else "签退",
            "record_time": record.record_time.strftime("%H:%M:%S") if record.record_time else None,
            "record_image": record.record_image,
            "status": record.status,
            "status_text": {"normal": "正常", "late": "迟到", "early": "早退"}.get(record.status, "未知")
        })
    
    return ResponseModel(
        data={"list": record_list, "total": total, "page": page, "page_size": page_size}
    )


@router.get("/statistics", response_model=ResponseModel)
async def get_statistics(
    user_id: Optional[int] = None,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """获取考勤统计"""
    stats = AttendanceService.get_statistics(
        db, user_id=user_id, start_date=start_date, end_date=end_date
    )
    
    return ResponseModel(
        data={
            "total_days": stats.total_days,
            "normal_days": stats.normal_days,
            "late_days": stats.late_days,
            "early_days": stats.early_days,
            "absent_days": stats.absent_days,
            "leave_days": stats.leave_days
        }
    )


@router.get("/my", response_model=ResponseModel)
async def get_my_attendances(
    page: int = 1,
    page_size: int = 10,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的考勤记录"""
    skip = (page - 1) * page_size
    records = AttendanceService.get_attendances(
        db, user_id=current_user.id, start_date=start_date, end_date=end_date,
        skip=skip, limit=page_size
    )
    total = AttendanceService.get_attendance_count(
        db, user_id=current_user.id, start_date=start_date, end_date=end_date
    )
    
    record_list = []
    for record in records:
        record_list.append({
            "id": record.id,
            "attendance_date": record.attendance_date.isoformat(),
            "record_type": record.record_type,
            "record_type_text": "签到" if record.record_type == "check_in" else "签退",
            "record_time": record.record_time.strftime("%H:%M:%S") if record.record_time else None,
            "status": record.status,
            "status_text": {"normal": "正常", "late": "迟到", "early": "早退"}.get(record.status, "未知")
        })
    
    return ResponseModel(
        data={"list": record_list, "total": total, "page": page, "page_size": page_size}
    )
