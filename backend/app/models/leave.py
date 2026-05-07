from sqlalchemy import Column, Integer, String, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class LeaveType(str, enum.Enum):
    PERSONAL = "personal"
    SICK = "sick"
    ANNUAL = "annual"


class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Leave(Base):
    """请假申请模型"""
    __tablename__ = "leaves"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    leave_type = Column(String(20), nullable=False, comment="请假类型: personal/sick/annual")
    start_date = Column(Date, nullable=False, comment="开始日期")
    end_date = Column(Date, nullable=False, comment="结束日期")
    reason = Column(Text, nullable=True, comment="请假原因")
    status = Column(String(20), default=LeaveStatus.PENDING.value, comment="状态: pending/approved/rejected")
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="审批人ID")
    approver_comment = Column(Text, nullable=True, comment="审批意见")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    user = relationship("User", back_populates="leaves", foreign_keys=[user_id])
    approver = relationship("User", foreign_keys=[approver_id])
