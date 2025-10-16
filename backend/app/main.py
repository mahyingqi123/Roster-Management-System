from datetime import date, timedelta
from io import StringIO
import csv
from typing import List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from . import models, schemas, crud


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Duty Roster Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Staff endpoints
@app.get("/staff", response_model=List[schemas.StaffRead])
def get_staff(db: Session = Depends(get_db)):
    return crud.list_staff(db)


@app.post("/staff", response_model=schemas.StaffRead, status_code=201)
def post_staff(payload: schemas.StaffCreate, db: Session = Depends(get_db)):
    return crud.create_staff(db, payload)


@app.delete("/staff/{staff_id}", status_code=204)
def remove_staff(staff_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_staff(db, staff_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Staff not found")
    return None


# Assignments and roster
@app.get("/roster")
def get_roster(start: date, end: date, db: Session = Depends(get_db)):
    rows = crud.list_assignments_in_range(db, start, end)
    # shape response
    return [
        {
            "assignment_id": a.id,
            "date": s.date,
            "shift_type": s.shift_type,
            "staff_id": st.id,
            "staff_name": st.name,
            "position": st.position,
        }
        for (a, s, st) in rows
    ]


@app.post("/assignments", response_model=schemas.AssignmentRead, status_code=201)
def post_assignment(payload: schemas.AssignmentCreate, db: Session = Depends(get_db)):
    try:
        created = crud.create_assignment(db, payload.date, payload.shift_type, payload.staff_id)
        return schemas.AssignmentRead(id=created.id, shift_id=created.shift_id, staff_id=created.staff_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/assignments/{assignment_id}", status_code=204)
def remove_assignment(assignment_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_assignment(db, assignment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return None


# Stats
@app.get("/stats/coverage", response_model=List[schemas.DayCoverage])
def get_coverage(start: date, end: date, db: Session = Depends(get_db)):
    return crud.coverage_stats(db, start, end)


@app.get("/stats/staff-load", response_model=List[schemas.StaffLoad])
def get_staff_load(start: date, end: date, db: Session = Depends(get_db)):
    return crud.staff_load_stats(db, start, end)


# Export CSV
@app.get("/export/roster.csv")
def export_roster_csv(start: date, end: date, db: Session = Depends(get_db)):
    rows = crud.list_assignments_in_range(db, start, end)
    sio = StringIO()
    writer = csv.writer(sio)
    writer.writerow(["date", "shift_type", "staff_id", "staff_name", "position"])
    for (a, s, st) in rows:
        writer.writerow([s.date.isoformat(), s.shift_type, st.id, st.name, st.position or ""]) 
    return {
        "filename": "roster.csv",
        "content": sio.getvalue(),
        "content_type": "text/csv",
    }


# Auto scheduling (simple heuristic)
@app.post("/schedule/auto")
def auto_schedule(payload: schemas.AutoScheduleRequest, db: Session = Depends(get_db)):
    staff_list = crud.list_staff(db)
    if not staff_list:
        raise HTTPException(status_code=400, detail="No staff available")

    # Build counters to balance load
    staff_id_to_count = {s.id: 0 for s in staff_list}

    current = payload.start
    created = []
    while current <= payload.end:
        for shift_type in payload.shift_types:
            # Assign up to min_per_shift distinct staff per shift
            for _ in range(payload.min_per_shift):
                # choose least-loaded staff
                sorted_staff = sorted(staff_list, key=lambda s: staff_id_to_count[s.id])
                chosen = None
                for st in sorted_staff:
                    try:
                        created_item = crud.create_assignment(db, current, shift_type, st.id)
                        staff_id_to_count[st.id] += 1
                        created.append(created_item.id)
                        chosen = st
                        break
                    except Exception:
                        # conflict or duplicate – try next staff
                        continue
                if chosen is None:
                    # nobody assignable for this slot
                    pass
        current += timedelta(days=1)

    return {"created_assignments": created}


