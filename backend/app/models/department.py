from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Department(Base):
    """部门模型"""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, comment="部门名称")
    description = Column(Text, nullable=True, comment="部门描述")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关联关系
    users = relationship("User", back_populates="department")
