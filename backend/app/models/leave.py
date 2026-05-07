from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Leave(Base):
    __tablename__ = "leaves"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="申请人ID")
    leave_type = Column(String(20), nullable=False, comment="请假类型: personal/sick/annual")
    start_date = Column(Date, nullable=False, comment="开始日期")
    end_date = Column(Date, nullable=False, comment="结束日期")
    reason = Column(Text, nullable=False, comment="请假原因")
    status = Column(String(20), default="pending", comment="状态: pending/approved/rejected")
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="审批人ID")
    approval_comment = Column(Text, nullable=True, comment="审批意见")
    approved_at = Column(DateTime, nullable=True, comment="审批时间")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")

    user = relationship("User", foreign_keys=[user_id], back_populates="leaves")
    approver = relationship("User", foreign_keys=[approver_id])
