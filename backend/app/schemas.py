from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# Staff
class StaffBase(BaseModel):
    name: str = Field(..., min_length=1)
    age: Optional[int] = None
    position: Optional[str] = None


class StaffCreate(StaffBase):
    pass


class StaffRead(StaffBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Shift
class ShiftBase(BaseModel):
    date: date
    shift_type: str


class ShiftCreate(ShiftBase):
    pass


class ShiftRead(ShiftBase):
    id: int

    class Config:
        from_attributes = True


# Assignment
class AssignmentBase(BaseModel):
    shift_id: int
    staff_id: int


class AssignmentCreate(BaseModel):
    date: date
    shift_type: str
    staff_id: int


class AssignmentRead(BaseModel):
    id: int
    shift_id: int
    staff_id: int

    class Config:
        from_attributes = True


# Queries & Stats
class DateRangeQuery(BaseModel):
    start: date
    end: date


class DayCoverage(BaseModel):
    date: date
    shift_type: str
    count: int


class StaffLoad(BaseModel):
    staff_id: int
    name: str
    total_assignments: int


class AutoScheduleRequest(BaseModel):
    start: date
    end: date
    shift_types: List[str] = Field(default_factory=lambda: ["morning", "afternoon", "night"])
    min_per_shift: int = 1


