from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Tuple
from datetime import datetime, date, time, timedelta
from app.models.attendance import Attendance
from app.models.user import User
from app.models.leave import Leave
from app.services.face_service import FaceService
from app.schemas.attendance import AttendanceStatistics
import logging

logger = logging.getLogger(__name__)

# 考勤时间配置
WORK_START_TIME = time(9, 0, 0)  # 上班时间 9:00
WORK_END_TIME = time(18, 0, 0)   # 下班时间 18:00


class AttendanceService:
    """考勤服务 - 每次打卡都创建新记录"""
    
    @staticmethod
    def check_in(db: Session, image_data: bytes) -> Tuple[bool, str, Optional[dict]]:
        """签到 - 每次都创建新记录"""
        # 人脸识别
        user, message = FaceService.recognize_face(db, image_data)
        if not user:
            return False, message, None
        
        today = date.today()
        now = datetime.now()
        
        # 保存签到照片
        image_path = FaceService.save_face_image(image_data, "checkin")
        
        # 判断是否迟到
        status = "normal"
        if now.time() > WORK_START_TIME:
            status = "late"
        
        # 创建新的签到记录
        attendance = Attendance(
            user_id=user.id,
            attendance_date=today,
            record_type="check_in",
            record_time=now,
            record_image=image_path,
            status=status
        )
        db.add(attendance)
        db.commit()
        
        status_text = "正常" if status == "normal" else "迟到"
        logger.info(f"用户 {user.real_name} 签到成功，状态: {status_text}")
        
        return True, f"签到成功 ({status_text})", {
            "user_name": user.real_name,
            "employee_no": user.employee_no,
            "record_time": now.strftime("%H:%M:%S"),
            "status": status_text
        }
    
    @staticmethod
    def check_out(db: Session, image_data: bytes) -> Tuple[bool, str, Optional[dict]]:
        """签退 - 每次都创建新记录"""
        # 人脸识别
        user, message = FaceService.recognize_face(db, image_data)
        if not user:
            return False, message, None
        
        today = date.today()
        now = datetime.now()
        
        # 保存签退照片
        image_path = FaceService.save_face_image(image_data, "checkout")
        
        # 判断是否早退
        status = "normal"
        if now.time() < WORK_END_TIME:
            status = "early"
        
        # 创建新的签退记录
        attendance = Attendance(
            user_id=user.id,
            attendance_date=today,
            record_type="check_out",
            record_time=now,
            record_image=image_path,
            status=status
        )
        db.add(attendance)
        db.commit()
        
        status_text = "正常" if status == "normal" else "早退"
        logger.info(f"用户 {user.real_name} 签退成功，状态: {status_text}")
        
        return True, f"签退成功 ({status_text})", {
            "user_name": user.real_name,
            "employee_no": user.employee_no,
            "record_time": now.strftime("%H:%M:%S"),
            "status": status_text
        }
    
    @staticmethod
    def check_in_with_user(db: Session, image_data: bytes, current_user: User) -> Tuple[bool, str, Optional[dict]]:
        """签到 - 验证人脸是否匹配当前登录用户"""
        is_match, message = FaceService.verify_face(db, image_data, current_user)
        if not is_match:
            return False, message, None
        
        today = date.today()
        now = datetime.now()
        
        # 保存签到照片
        image_path = FaceService.save_face_image(image_data, "checkin")
        
        # 判断是否迟到
        status = "normal"
        if now.time() > WORK_START_TIME:
            status = "late"
        
        # 创建新的签到记录
        attendance = Attendance(
            user_id=current_user.id,
            attendance_date=today,
            record_type="check_in",
            record_time=now,
            record_image=image_path,
            status=status
        )
        db.add(attendance)
        db.commit()
        
        status_text = "正常" if status == "normal" else "迟到"
        logger.info(f"用户 {current_user.real_name} 签到成功，状态: {status_text}")
        
        return True, f"签到成功 ({status_text})", {
            "user_name": current_user.real_name,
            "employee_no": current_user.employee_no,
            "record_time": now.strftime("%H:%M:%S"),
            "status": status_text
        }
    
    @staticmethod
    def check_out_with_user(db: Session, image_data: bytes, current_user: User) -> Tuple[bool, str, Optional[dict]]:
        """签退 - 验证人脸是否匹配当前登录用户"""
        is_match, message = FaceService.verify_face(db, image_data, current_user)
        if not is_match:
            return False, message, None
        
        today = date.today()
        now = datetime.now()
        
        # 保存签退照片
        image_path = FaceService.save_face_image(image_data, "checkout")
        
        # 判断是否早退
        status = "normal"
        if now.time() < WORK_END_TIME:
            status = "early"
        
        # 创建新的签退记录
        attendance = Attendance(
            user_id=current_user.id,
            attendance_date=today,
            record_type="check_out",
            record_time=now,
            record_image=image_path,
            status=status
        )
        db.add(attendance)
        db.commit()
        
        status_text = "正常" if status == "normal" else "早退"
        logger.info(f"用户 {current_user.real_name} 签退成功，状态: {status_text}")
        
        return True, f"签退成功 ({status_text})", {
            "user_name": current_user.real_name,
            "employee_no": current_user.employee_no,
            "record_time": now.strftime("%H:%M:%S"),
            "status": status_text
        }
    
    @staticmethod
    def get_attendances(
        db: Session,
        user_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Attendance]:
        """获取考勤记录"""
        query = db.query(Attendance)
        
        if user_id:
            query = query.filter(Attendance.user_id == user_id)
        if start_date:
            query = query.filter(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.filter(Attendance.attendance_date <= end_date)
        
        return query.order_by(Attendance.record_time.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_attendance_count(
        db: Session,
        user_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> int:
        """获取考勤记录总数"""
        query = db.query(Attendance)
        
        if user_id:
            query = query.filter(Attendance.user_id == user_id)
        if start_date:
            query = query.filter(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.filter(Attendance.attendance_date <= end_date)
        
        return query.count()
    
    @staticmethod
    def get_statistics(
        db: Session,
        user_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> AttendanceStatistics:
        query = db.query(Attendance)

        if user_id:
            query = query.filter(Attendance.user_id == user_id)
        if start_date:
            query = query.filter(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.filter(Attendance.attendance_date <= end_date)

        records = query.all()

        leave_days = 0
        if start_date and end_date:
            uid = user_id
            if uid:
                leave_query = db.query(Leave).filter(
                    Leave.user_id == uid,
                    Leave.status == "approved",
                    Leave.start_date <= end_date,
                    Leave.end_date >= start_date,
                ).all()
                leave_dates = set()
                for lv in leave_query:
                    current = max(lv.start_date, start_date)
                    bound = min(lv.end_date, end_date)
                    while current <= bound:
                        leave_dates.add(current)
                        current = current + timedelta(days=1)
                leave_days = len(leave_dates)

        stats = AttendanceStatistics(
            total_days=len(records),
            normal_days=sum(1 for r in records if r.status == "normal"),
            late_days=sum(1 for r in records if r.status == "late"),
            early_days=sum(1 for r in records if r.status == "early"),
            absent_days=0,
            leave_days=leave_days
        )

        return stats
