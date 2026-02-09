import face_recognition
import numpy as np
import json
import os
import uuid
from PIL import Image
from io import BytesIO
from sqlalchemy.orm import Session
from typing import Optional, Tuple, List
from app.models.face_encoding import FaceEncoding
from app.models.user import User
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class FaceService:
    """人脸识别服务"""
    
    @staticmethod
    def ensure_upload_dir():
        """确保上传目录存在"""
        if not os.path.exists(settings.UPLOAD_DIR):
            os.makedirs(settings.UPLOAD_DIR)
        faces_dir = os.path.join(settings.UPLOAD_DIR, "faces")
        if not os.path.exists(faces_dir):
            os.makedirs(faces_dir)
        attendance_dir = os.path.join(settings.UPLOAD_DIR, "attendance")
        if not os.path.exists(attendance_dir):
            os.makedirs(attendance_dir)
    
    @staticmethod
    def extract_face_encoding(image_data: bytes) -> Optional[np.ndarray]:
        """从图片中提取人脸编码"""
        try:
            image = Image.open(BytesIO(image_data))
            if image.mode != "RGB":
                image = image.convert("RGB")
            image_array = np.array(image)
            face_locations = face_recognition.face_locations(image_array)
            if not face_locations:
                return None
            face_encodings = face_recognition.face_encodings(image_array, face_locations)
            if not face_encodings:
                return None
            return face_encodings[0]
        except Exception as e:
            logger.error(f"提取人脸编码失败: {str(e)}")
            return None
    
    @staticmethod
    def save_face_image(image_data: bytes, prefix: str = "face") -> str:
        """保存人脸图片"""
        FaceService.ensure_upload_dir()
        filename = f"{prefix}_{uuid.uuid4().hex}.jpg"
        if prefix == "face":
            filepath = os.path.join(settings.UPLOAD_DIR, "faces", filename)
        else:
            filepath = os.path.join(settings.UPLOAD_DIR, "attendance", filename)
        
        image = Image.open(BytesIO(image_data))
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(filepath, "JPEG", quality=85)
        return filepath
    
    @staticmethod
    def register_face(db: Session, user_id: int, image_data: bytes) -> Tuple[bool, str]:
        """注册人脸"""
        encoding = FaceService.extract_face_encoding(image_data)
        if encoding is None:
            return False, "未检测到人脸，请确保照片中有清晰的人脸"
        
        # 检查是否已存在人脸
        existing = db.query(FaceEncoding).filter(FaceEncoding.user_id == user_id).first()
        if existing:
            # 删除旧的人脸数据
            if os.path.exists(existing.image_path):
                os.remove(existing.image_path)
            db.delete(existing)
        
        # 保存图片
        image_path = FaceService.save_face_image(image_data, "face")
        
        # 保存编码
        encoding_json = json.dumps(encoding.tolist())
        face_encoding = FaceEncoding(
            user_id=user_id,
            encoding_data=encoding_json,
            image_path=image_path
        )
        db.add(face_encoding)
        db.commit()
        
        logger.info(f"用户 {user_id} 人脸注册成功")
        return True, "人脸注册成功"
    
    @staticmethod
    def recognize_face(db: Session, image_data: bytes) -> Tuple[Optional[User], str]:
        """识别人脸"""
        encoding = FaceService.extract_face_encoding(image_data)
        if encoding is None:
            return None, "未检测到人脸"
        
        # 获取所有已注册的人脸编码
        all_encodings = db.query(FaceEncoding).all()
        if not all_encodings:
            return None, "系统中没有已注册的人脸"
        
        known_encodings = []
        user_ids = []
        for fe in all_encodings:
            try:
                enc = np.array(json.loads(fe.encoding_data))
                known_encodings.append(enc)
                user_ids.append(fe.user_id)
            except Exception as e:
                logger.error(f"解析人脸编码失败: {str(e)}")
                continue
        
        if not known_encodings:
            return None, "没有有效的人脸数据"
        
        # 比对人脸
        distances = face_recognition.face_distance(known_encodings, encoding)
        min_distance_idx = np.argmin(distances)
        min_distance = distances[min_distance_idx]
        
        if min_distance <= settings.FACE_RECOGNITION_TOLERANCE:
            user_id = user_ids[min_distance_idx]
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.is_active:
                return user, "识别成功"
            return None, "用户已被禁用"
        
        return None, "人脸不匹配"
    
    @staticmethod
    def verify_face(db: Session, image_data: bytes, user: User) -> Tuple[bool, str]:
        """验证人脸是否匹配指定用户"""
        encoding = FaceService.extract_face_encoding(image_data)
        if encoding is None:
            return False, "未检测到人脸，请正对摄像头"
        
        # 获取用户的人脸编码
        face_encoding = db.query(FaceEncoding).filter(FaceEncoding.user_id == user.id).first()
        if not face_encoding:
            return False, "您尚未录入人脸信息"
        
        try:
            known_encoding = np.array(json.loads(face_encoding.encoding_data))
        except Exception as e:
            logger.error(f"解析人脸编码失败: {str(e)}")
            return False, "人脸数据异常，请重新录入"
        
        # 比对人脸
        distance = face_recognition.face_distance([known_encoding], encoding)[0]
        
        if distance <= settings.FACE_RECOGNITION_TOLERANCE:
            return True, "人脸验证成功"
        
        return False, "人脸验证失败，请确保是本人操作"
    
    @staticmethod
    def get_all_face_encodings(db: Session) -> List[Tuple[int, np.ndarray]]:
        """获取所有人脸编码"""
        all_encodings = db.query(FaceEncoding).all()
        result = []
        for fe in all_encodings:
            try:
                enc = np.array(json.loads(fe.encoding_data))
                result.append((fe.user_id, enc))
            except Exception:
                continue
        return result
