from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="部门名称")
    description: Optional[str] = Field(None, max_length=500, description="部门描述")


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class DepartmentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    user_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True
