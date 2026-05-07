from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, date


class LeaveCreate(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: str

    @field_validator("leave_type")
    @classmethod
    def validate_leave_type(cls, v):
        if v not in ("personal", "sick", "annual"):
            raise ValueError("请假类型必须为 personal/sick/annual")
        return v

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, v, info):
        if info.data.get("start_date") and v < info.data["start_date"]:
            raise ValueError("结束日期不能早于开始日期")
        return v


class LeaveApprove(BaseModel):
    status: str
    approval_comment: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v not in ("approved", "rejected"):
            raise ValueError("审批状态必须为 approved/rejected")
        return v


class LeaveResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    employee_no: Optional[str] = None
    department_name: Optional[str] = None
    leave_type: str
    leave_type_text: Optional[str] = None
    start_date: date
    end_date: date
    reason: str
    status: str
    status_text: Optional[str] = None
    approver_id: Optional[int] = None
    approver_name: Optional[str] = None
    approval_comment: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
