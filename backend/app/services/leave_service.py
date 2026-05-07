from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Tuple
from datetime import date, datetime
from app.models.leave import Leave, LeaveType, LeaveStatus
from app.models.user import User
from app.schemas.leave import LeaveCreate, LEAVE_TYPE_TEXT, LEAVE_STATUS_TEXT
import logging

logger = logging.getLogger(__name__)


class LeaveService:
    """请假服务"""

    @staticmethod
    def check_time_conflict(
        db: Session,
        user_id: int,
        start_date: date,
        end_date: date,
        exclude_leave_id: Optional[int] = None
    ) -> bool:
        """检查时间段是否与现有请假冲突"""
        query = db.query(Leave).filter(
            Leave.user_id == user_id,
            Leave.status.in_([LeaveStatus.PENDING.value, LeaveStatus.APPROVED.value])
        )
        
        if exclude_leave_id:
            query = query.filter(Leave.id != exclude_leave_id)
        
        existing_leaves = query.all()
        
        for leave in existing_leaves:
            if not (end_date < leave.start_date or start_date > leave.end_date):
                return True
        
        return False

    @staticmethod
    def create_leave(db: Session, user_id: int, leave_data: LeaveCreate) -> Tuple[bool, str, Optional[Leave]]:
        """创建请假申请"""
        if leave_data.start_date > leave_data.end_date:
            return False, "开始日期不能晚于结束日期", None
        
        if leave_data.start_date < date.today():
            return False, "开始日期不能早于今天", None
        
        if leave_data.leave_type not in [t.value for t in LeaveType]:
            return False, f"无效的请假类型: {leave_data.leave_type}", None
        
        if LeaveService.check_time_conflict(db, user_id, leave_data.start_date, leave_data.end_date):
            return False, "该时间段已有待审批或已通过的请假申请", None
        
        leave = Leave(
            user_id=user_id,
            leave_type=leave_data.leave_type,
            start_date=leave_data.start_date,
            end_date=leave_data.end_date,
            reason=leave_data.reason,
            status=LeaveStatus.PENDING.value
        )
        db.add(leave)
        db.commit()
        db.refresh(leave)
        
        logger.info(f"用户 {user_id} 提交请假申请: {leave.id}")
        return True, "请假申请提交成功", leave

    @staticmethod
    def get_user_leaves(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Leave]:
        """获取用户的请假记录"""
        query = db.query(Leave).filter(Leave.user_id == user_id)
        
        if status:
            query = query.filter(Leave.status == status)
        
        return query.order_by(Leave.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_leave_count(
        db: Session,
        user_id: int,
        status: Optional[str] = None
    ) -> int:
        """获取用户请假记录总数"""
        query = db.query(Leave).filter(Leave.user_id == user_id)
        
        if status:
            query = query.filter(Leave.status == status)
        
        return query.count()

    @staticmethod
    def get_all_leaves(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> List[Leave]:
        """获取所有请假记录（管理员）"""
        query = db.query(Leave)
        
        if status:
            query = query.filter(Leave.status == status)
        if user_id:
            query = query.filter(Leave.user_id == user_id)
        
        return query.order_by(Leave.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_leave_count(
        db: Session,
        status: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> int:
        """获取所有请假记录总数（管理员）"""
        query = db.query(Leave)
        
        if status:
            query = query.filter(Leave.status == status)
        if user_id:
            query = query.filter(Leave.user_id == user_id)
        
        return query.count()

    @staticmethod
    def get_leave_by_id(db: Session, leave_id: int) -> Optional[Leave]:
        """根据ID获取请假记录"""
        return db.query(Leave).filter(Leave.id == leave_id).first()

    @staticmethod
    def approve_leave(
        db: Session,
        leave_id: int,
        approver_id: int,
        approved: bool,
        comment: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Leave]]:
        """审批请假申请"""
        leave = db.query(Leave).filter(Leave.id == leave_id).first()
        
        if not leave:
            return False, "请假申请不存在", None
        
        if leave.status != LeaveStatus.PENDING.value:
            return False, "该请假申请已被审批", None
        
        leave.status = LeaveStatus.APPROVED.value if approved else LeaveStatus.REJECTED.value
        leave.approver_id = approver_id
        leave.approver_comment = comment
        
        db.commit()
        db.refresh(leave)
        
        action = "通过" if approved else "驳回"
        logger.info(f"审批人 {approver_id} {action}了请假申请 {leave_id}")
        return True, f"请假申请已{action}", leave

    @staticmethod
    def is_user_on_leave(db: Session, user_id: int, check_date: date) -> bool:
        """检查用户在指定日期是否有已通过的请假"""
        leave = db.query(Leave).filter(
            Leave.user_id == user_id,
            Leave.status == LeaveStatus.APPROVED.value,
            Leave.start_date <= check_date,
            Leave.end_date >= check_date
        ).first()
        
        return leave is not None

    @staticmethod
    def format_leave_response(leave: Leave) -> dict:
        """格式化请假记录响应"""
        user = leave.user
        dept_name = user.department.name if user and user.department else None
        approver_name = leave.approver.real_name if leave.approver else None
        
        return {
            "id": leave.id,
            "user_id": leave.user_id,
            "user_name": user.real_name if user else None,
            "employee_no": user.employee_no if user else None,
            "department_name": dept_name,
            "leave_type": leave.leave_type,
            "leave_type_text": LEAVE_TYPE_TEXT.get(leave.leave_type, leave.leave_type),
            "start_date": leave.start_date.isoformat(),
            "end_date": leave.end_date.isoformat(),
            "reason": leave.reason,
            "status": leave.status,
            "status_text": LEAVE_STATUS_TEXT.get(leave.status, leave.status),
            "approver_id": leave.approver_id,
            "approver_name": approver_name,
            "approver_comment": leave.approver_comment,
            "created_at": leave.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": leave.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
