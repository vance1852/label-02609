from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Tuple
from datetime import datetime, date, timedelta
from app.models.leave import Leave
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

LEAVE_TYPE_MAP = {"personal": "事假", "sick": "病假", "annual": "年假"}
STATUS_MAP = {"pending": "待审批", "approved": "已通过", "rejected": "已驳回"}


class LeaveService:

    @staticmethod
    def create_leave(db: Session, user_id: int, leave_type: str, start_date: date, end_date: date, reason: str) -> Tuple[bool, str, Optional[Leave]]:
        overlap = db.query(Leave).filter(
            Leave.user_id == user_id,
            Leave.status.in_(["pending", "approved"]),
            or_(
                and_(Leave.start_date <= start_date, Leave.end_date >= start_date),
                and_(Leave.start_date <= end_date, Leave.end_date >= end_date),
                and_(Leave.start_date >= start_date, Leave.end_date <= end_date),
            )
        ).first()

        if overlap:
            return False, "该时间段内已有请假申请，不可重复提交", None

        leave = Leave(
            user_id=user_id,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            status="pending"
        )
        db.add(leave)
        db.commit()
        db.refresh(leave)
        logger.info(f"用户 {user_id} 提交请假申请 {leave.id}")
        return True, "请假申请提交成功", leave

    @staticmethod
    def get_my_leaves(
        db: Session, user_id: int,
        status: Optional[str] = None,
        skip: int = 0, limit: int = 20
    ) -> Tuple[List[dict], int]:
        query = db.query(Leave).filter(Leave.user_id == user_id)
        if status:
            query = query.filter(Leave.status == status)
        total = query.count()
        leaves = query.order_by(Leave.created_at.desc()).offset(skip).limit(limit).all()
        result = [LeaveService._to_dict(leave) for leave in leaves]
        return result, total

    @staticmethod
    def get_pending_leaves(
        db: Session,
        skip: int = 0, limit: int = 20
    ) -> Tuple[List[dict], int]:
        query = db.query(Leave).filter(Leave.status == "pending")
        total = query.count()
        leaves = query.order_by(Leave.created_at.asc()).offset(skip).limit(limit).all()
        result = [LeaveService._to_dict(leave) for leave in leaves]
        return result, total

    @staticmethod
    def get_all_leaves(
        db: Session,
        status: Optional[str] = None,
        user_id: Optional[int] = None,
        skip: int = 0, limit: int = 20
    ) -> Tuple[List[dict], int]:
        query = db.query(Leave)
        if status:
            query = query.filter(Leave.status == status)
        if user_id:
            query = query.filter(Leave.user_id == user_id)
        total = query.count()
        leaves = query.order_by(Leave.created_at.desc()).offset(skip).limit(limit).all()
        result = [LeaveService._to_dict(leave) for leave in leaves]
        return result, total

    @staticmethod
    def approve_leave(
        db: Session, leave_id: int, approver_id: int,
        status: str, approval_comment: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Leave]]:
        leave = db.query(Leave).filter(Leave.id == leave_id).first()
        if not leave:
            return False, "请假申请不存在", None
        if leave.status != "pending":
            return False, "该请假申请已处理", None

        leave.status = status
        leave.approver_id = approver_id
        leave.approval_comment = approval_comment
        leave.approved_at = datetime.now()
        db.commit()
        db.refresh(leave)

        action = "通过" if status == "approved" else "驳回"
        logger.info(f"审批人 {approver_id} {action}请假申请 {leave_id}")
        return True, f"请假申请已{action}", leave

    @staticmethod
    def get_approved_leave_dates(db: Session, user_id: int, start_date: date, end_date: date) -> List[date]:
        leaves = db.query(Leave).filter(
            Leave.user_id == user_id,
            Leave.status == "approved",
            Leave.start_date <= end_date,
            Leave.end_date >= start_date,
        ).all()
        dates = set()
        for leave in leaves:
            current = max(leave.start_date, start_date)
            bound = min(leave.end_date, end_date)
            while current <= bound:
                dates.add(current)
                current = current + timedelta(days=1)
        return sorted(dates)

    @staticmethod
    def _to_dict(leave: Leave) -> dict:
        user = leave.user
        approver = leave.approver
        dept_name = user.department.name if user and user.department else None
        return {
            "id": leave.id,
            "user_id": leave.user_id,
            "user_name": user.real_name if user else None,
            "employee_no": user.employee_no if user else None,
            "department_name": dept_name,
            "leave_type": leave.leave_type,
            "leave_type_text": LEAVE_TYPE_MAP.get(leave.leave_type, leave.leave_type),
            "start_date": leave.start_date.isoformat(),
            "end_date": leave.end_date.isoformat(),
            "reason": leave.reason,
            "status": leave.status,
            "status_text": STATUS_MAP.get(leave.status, leave.status),
            "approver_id": leave.approver_id,
            "approver_name": approver.real_name if approver else None,
            "approval_comment": leave.approval_comment,
            "approved_at": leave.approved_at.isoformat() if leave.approved_at else None,
            "created_at": leave.created_at.isoformat() if leave.created_at else None,
        }
