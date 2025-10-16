from datetime import date
from typing import Iterable, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from . import models, schemas


# Staff
def list_staff(db: Session) -> List[models.Staff]:
    return db.query(models.Staff).order_by(models.Staff.id.asc()).all()


def create_staff(db: Session, staff: schemas.StaffCreate) -> models.Staff:
    obj = models.Staff(name=staff.name, age=staff.age, position=staff.position)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def delete_staff(db: Session, staff_id: int) -> bool:
    obj = db.query(models.Staff).get(staff_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# Shifts
def get_or_create_shift(db: Session, d: date, shift_type: str) -> models.Shift:
    shift = (
        db.query(models.Shift)
        .filter(models.Shift.date == d, models.Shift.shift_type == shift_type)
        .first()
    )
    if shift:
        return shift
    shift = models.Shift(date=d, shift_type=shift_type)
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift


# Assignments
def list_assignments_in_range(db: Session, start: date, end: date) -> List[Tuple[models.Assignment, models.Shift, models.Staff]]:
    q = (
        db.query(models.Assignment, models.Shift, models.Staff)
        .join(models.Shift, models.Assignment.shift_id == models.Shift.id)
        .join(models.Staff, models.Assignment.staff_id == models.Staff.id)
        .filter(models.Shift.date >= start, models.Shift.date <= end)
        .order_by(models.Shift.date.asc(), models.Shift.shift_type.asc())
    )
    return q.all()


def create_assignment(db: Session, date_value: date, shift_type: str, staff_id: int) -> models.Assignment:
    shift = get_or_create_shift(db, date_value, shift_type)
    assign = models.Assignment(shift_id=shift.id, staff_id=staff_id)
    db.add(assign)
    db.commit()
    db.refresh(assign)
    return assign


def delete_assignment(db: Session, assignment_id: int) -> bool:
    obj = db.query(models.Assignment).get(assignment_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True


# Stats
def coverage_stats(db: Session, start: date, end: date) -> List[schemas.DayCoverage]:
    q = (
        db.query(models.Shift.date, models.Shift.shift_type, func.count(models.Assignment.id))
        .outerjoin(models.Assignment, models.Assignment.shift_id == models.Shift.id)
        .filter(models.Shift.date >= start, models.Shift.date <= end)
        .group_by(models.Shift.date, models.Shift.shift_type)
        .order_by(models.Shift.date.asc(), models.Shift.shift_type.asc())
    )
    return [
        schemas.DayCoverage(date=row[0], shift_type=row[1], count=row[2])
        for row in q.all()
    ]


def staff_load_stats(db: Session, start: date, end: date) -> List[schemas.StaffLoad]:
    q = (
        db.query(models.Staff.id, models.Staff.name, func.count(models.Assignment.id))
        .outerjoin(models.Assignment, models.Assignment.staff_id == models.Staff.id)
        .outerjoin(models.Shift, models.Assignment.shift_id == models.Shift.id)
        .filter(or_(models.Shift.date == None, and_(models.Shift.date >= start, models.Shift.date <= end)))
        .group_by(models.Staff.id, models.Staff.name)
        .order_by(models.Staff.id.asc())
    )
    return [
        schemas.StaffLoad(staff_id=row[0], name=row[1], total_assignments=row[2])
        for row in q.all()
    ]


