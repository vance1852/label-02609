"""
数据库初始化脚本
创建默认管理员账户和示例部门
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.models import User, Department, FaceEncoding, Attendance, Leave
from app.core.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表创建完成")
    
    db = SessionLocal()
    try:
        # 检查是否已有管理员
        admin = db.query(User).filter(User.username == "admin").first()
        if admin:
            logger.info("管理员账户已存在，跳过初始化")
            return
        
        # 创建默认部门
        departments = [
            Department(name="技术部", description="负责技术研发"),
            Department(name="产品部", description="负责产品设计"),
            Department(name="运营部", description="负责运营推广"),
        ]
        for dept in departments:
            db.add(dept)
        db.commit()
        logger.info("默认部门创建完成")
        
        # 获取技术部ID
        tech_dept = db.query(Department).filter(Department.name == "技术部").first()
        
        # 创建管理员账户
        admin = User(
            username="admin",
            password=get_password_hash("admin123"),
            real_name="系统管理员",
            employee_no="EMP001",
            department_id=tech_dept.id,
            role="admin",
            is_active=True
        )
        db.add(admin)
        
        # 创建测试用户
        test_user = User(
            username="zhangsan",
            password=get_password_hash("123456"),
            real_name="张三",
            employee_no="EMP002",
            department_id=tech_dept.id,
            role="user",
            is_active=True
        )
        db.add(test_user)
        
        db.commit()
        logger.info("默认用户创建完成")
        logger.info("管理员账户: admin / admin123")
        logger.info("测试账户: zhangsan / 123456")
        
    except Exception as e:
        logger.error(f"初始化失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
