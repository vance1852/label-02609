from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from app.models.user import User
from app.models.face_encoding import FaceEncoding
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import get_password_hash, verify_password
import logging

logger = logging.getLogger(__name__)


class UserService:
    """用户服务"""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100, keyword: str = None) -> List[User]:
        """获取用户列表"""
        query = db.query(User)
        if keyword:
            query = query.filter(
                or_(
                    User.username.like(f"%{keyword}%"),
                    User.real_name.like(f"%{keyword}%"),
                    User.employee_no.like(f"%{keyword}%")
                )
            )
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_count(db: Session, keyword: str = None) -> int:
        """获取用户总数"""
        query = db.query(User)
        if keyword:
            query = query.filter(
                or_(
                    User.username.like(f"%{keyword}%"),
                    User.real_name.like(f"%{keyword}%"),
                    User.employee_no.like(f"%{keyword}%")
                )
            )
        return query.count()
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """创建用户"""
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            password=hashed_password,
            real_name=user_data.real_name,
            employee_no=user_data.employee_no,
            department_id=user_data.department_id,
            role=user_data.role
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"创建用户: {user_data.username}")
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """更新用户"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            update_data["password"] = get_password_hash(update_data["password"])
        
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
        logger.info(f"更新用户: {db_user.username}")
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """删除用户"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
        
        logger.info(f"删除用户: {db_user.username}")
        db.delete(db_user)
        db.commit()
        return True
    
    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> Optional[User]:
        """验证用户"""
        user = UserService.get_user_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user
    
    @staticmethod
    def user_has_face(db: Session, user_id: int) -> bool:
        """检查用户是否已录入人脸"""
        return db.query(FaceEncoding).filter(FaceEncoding.user_id == user_id).first() is not None
