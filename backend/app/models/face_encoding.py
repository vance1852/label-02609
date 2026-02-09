from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class FaceEncoding(Base):
    """人脸编码模型"""
    __tablename__ = "face_encodings"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    encoding_data = Column(Text, nullable=False, comment="人脸编码数据(JSON)")
    image_path = Column(String(255), nullable=False, comment="人脸图片路径")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    # 关联关系
    user = relationship("User", back_populates="face_encodings")
