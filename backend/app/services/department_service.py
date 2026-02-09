from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.department import Department
from app.models.user import User
from app.schemas.department import DepartmentCreate, DepartmentUpdate
import logging

logger = logging.getLogger(__name__)


class DepartmentService:
    """部门服务"""
    
    @staticmethod
    def get_department_by_id(db: Session, dept_id: int) -> Optional[Department]:
        """根据ID获取部门"""
        return db.query(Department).filter(Department.id == dept_id).first()
    
    @staticmethod
    def get_department_by_name(db: Session, name: str) -> Optional[Department]:
        """根据名称获取部门"""
        return db.query(Department).filter(Department.name == name).first()
    
    @staticmethod
    def get_departments(db: Session, skip: int = 0, limit: int = 100) -> List[Department]:
        """获取部门列表"""
        return db.query(Department).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_department_count(db: Session) -> int:
        """获取部门总数"""
        return db.query(Department).count()
    
    @staticmethod
    def get_user_count_by_department(db: Session, dept_id: int) -> int:
        """获取部门下的用户数量"""
        return db.query(User).filter(User.department_id == dept_id).count()
    
    @staticmethod
    def create_department(db: Session, dept_data: DepartmentCreate) -> Department:
        """创建部门"""
        db_dept = Department(
            name=dept_data.name,
            description=dept_data.description
        )
        db.add(db_dept)
        db.commit()
        db.refresh(db_dept)
        logger.info(f"创建部门: {dept_data.name}")
        return db_dept
    
    @staticmethod
    def update_department(db: Session, dept_id: int, dept_data: DepartmentUpdate) -> Optional[Department]:
        """更新部门"""
        db_dept = db.query(Department).filter(Department.id == dept_id).first()
        if not db_dept:
            return None
        
        update_data = dept_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_dept, key, value)
        
        db.commit()
        db.refresh(db_dept)
        logger.info(f"更新部门: {db_dept.name}")
        return db_dept
    
    @staticmethod
    def delete_department(db: Session, dept_id: int) -> bool:
        """删除部门"""
        db_dept = db.query(Department).filter(Department.id == dept_id).first()
        if not db_dept:
            return False
        
        # 检查是否有用户
        user_count = DepartmentService.get_user_count_by_department(db, dept_id)
        if user_count > 0:
            raise ValueError(f"部门下还有 {user_count} 名员工，无法删除")
        
        logger.info(f"删除部门: {db_dept.name}")
        db.delete(db_dept)
        db.commit()
        return True
