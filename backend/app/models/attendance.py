from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Attendance(Base):
    """考勤记录模型 - 每次打卡创建一条记录"""
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    attendance_date = Column(Date, nullable=False, comment="考勤日期")
    record_type = Column(String(20), default="check_in", comment="记录类型: check_in/check_out")
    record_time = Column(DateTime, nullable=False, comment="打卡时间")
    record_image = Column(String(255), nullable=True, comment="打卡照片")
    status = Column(String(20), default="normal", comment="状态: normal/late/early")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关联关系
    user = relationship("User", back_populates="attendances")
