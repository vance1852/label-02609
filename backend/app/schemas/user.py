from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    real_name: str = Field(..., min_length=2, max_length=50, description="真实姓名")
    employee_no: str = Field(..., min_length=1, max_length=50, description="工号")
    department_id: Optional[int] = Field(None, description="部门ID")
    role: str = Field(default="user", description="角色")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50, description="密码")


class UserUpdate(BaseModel):
    real_name: Optional[str] = Field(None, min_length=2, max_length=50)
    department_id: Optional[int] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6, max_length=50)


class UserResponse(BaseModel):
    id: int
    username: str
    real_name: str
    employee_no: str
    department_id: Optional[int]
    department_name: Optional[str] = None
    role: str
    is_active: bool
    has_face: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
