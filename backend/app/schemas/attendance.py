from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    user_name: Optional[str] = None
    employee_no: Optional[str] = None
    department_name: Optional[str] = None
    attendance_date: date
    check_in_time: Optional[datetime]
    check_out_time: Optional[datetime]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AttendanceStatistics(BaseModel):
    total_days: int = 0
    normal_days: int = 0
    late_days: int = 0
    early_days: int = 0
    absent_days: int = 0
    leave_days: int = 0
