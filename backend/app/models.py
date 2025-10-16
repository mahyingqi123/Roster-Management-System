from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .database import Base


class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    age = Column(Integer, nullable=True)
    position = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    assignments = relationship("Assignment", back_populates="staff", cascade="all, delete-orphan")


class Shift(Base):
    __tablename__ = "shift"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    shift_type = Column(String(50), nullable=False, index=True)

    assignments = relationship("Assignment", back_populates="shift", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("date", "shift_type", name="uq_shift_date_type"),
    )


class Assignment(Base):
    __tablename__ = "assignment"

    id = Column(Integer, primary_key=True, index=True)
    shift_id = Column(Integer, ForeignKey("shift.id", ondelete="CASCADE"), nullable=False)
    staff_id = Column(Integer, ForeignKey("staff.id", ondelete="CASCADE"), nullable=False)

    shift = relationship("Shift", back_populates="assignments")
    staff = relationship("Staff", back_populates="assignments")

    __table_args__ = (
        UniqueConstraint("shift_id", "staff_id", name="uq_assignment_unique"),
    )


