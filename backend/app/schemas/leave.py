from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from app.models.leave import LeaveType, LeaveStatus


class LeaveCreate(BaseModel):
    leave_type: str = Field(..., description="请假类型: personal/sick/annual")
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    reason: Optional[str] = Field(None, description="请假原因")


class LeaveApprove(BaseModel):
    comment: Optional[str] = Field(None, description="审批意见")


class LeaveResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    employee_no: Optional[str] = None
    department_name: Optional[str] = None
    leave_type: str
    leave_type_text: str
    start_date: date
    end_date: date
    reason: Optional[str] = None
    status: str
    status_text: str
    approver_id: Optional[int] = None
    approver_name: Optional[str] = None
    approver_comment: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


LEAVE_TYPE_TEXT = {
    LeaveType.PERSONAL.value: "事假",
    LeaveType.SICK.value: "病假",
    LeaveType.ANNUAL.value: "年假"
}

LEAVE_STATUS_TEXT = {
    LeaveStatus.PENDING.value: "待审批",
    LeaveStatus.APPROVED.value: "已通过",
    LeaveStatus.REJECTED.value: "已驳回"
}
