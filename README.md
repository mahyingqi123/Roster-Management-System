# Roster-Management-System
A duty roster management system using FastAPI and Vue.js


### Overview
This project manages on-duty staff, supports manual and automatic scheduling, and provides a web UI to view schedules and statistics. The backend is built with FastAPI and a relational database via an ORM, and the frontend is built with Vue.js.

### Video Demo

https://github.com/user-attachments/assets/4378053a-c724-46cb-8c3d-0722c9cecd91


### Requirements (需求)
- 设计一个值班人员管理系统，实现以下功能：
  - 值班人员信息管理（增删），姓名、年龄、职位即可。
  - 值班排班功能，根据值班人员进行排班。
  - 值班情况统计和前端展示。
- 附加题：
  - 排班表导出功能。
  - 自动排班算法，根据员工数量以及工作日自动分配排班。
- 要体现面向对象思想，要使用到数据库。
- 语言要求：后端：python；前端：vue.js。


### Core Features
- Staff Information Management: Add and delete staff members. Required fields: Name, Age, Position.
- Roster Scheduling: Manually assign staff members to shifts (e.g., by date and shift type).
- Roster Statistics and Frontend Display: View the duty roster and related statistics on the web UI.


### Bonus Features
- Roster Export: Export the schedule to a file (e.g., CSV).
- Automatic Scheduling: Automatically generate a schedule based on the number of employees and working days.


### Tech Stack
- Backend: FastAPI (Python), ORM (e.g., SQLAlchemy), Pydantic for schema validation
- Database: Relational DB (e.g., SQLite for local dev, can switch to Postgres/MySQL)
- Frontend: Vue.js (Vite or Vue CLI)
- Containerization: Docker + Docker Compose


### Project Structure

```text
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py       # API 入口
│   │   ├── models.py     # ORM 模型
│   │   ├── schemas.py    # Pydantic 数据校验模型
│   │   └── crud.py       # 数据库增删改查操作
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── StaffManagement.vue
│   │   │   └── RosterDisplay.vue
│   │   ├── App.vue
│   │   └── main.js
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml
```


### Getting Started

#### Quick start (local scripts)
- Starts Postgres via Docker, runs backend (FastAPI) and frontend (Vite) locally.

```bash
scripts/start_db.sh
scripts/run_backend_local.sh  
scripts/run_frontend_local.sh  
```

### Run with Docker Compose

- Build and start services:

```bash
docker compose up --build -d
```

### Local Development 

- Backend:
```bash
cd backend
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

- Frontend:

```bash
cd frontend
npm install
npm run dev
```


### Database Schema (proposed)
- Table: `staff`
  - `id` (int, PK)
  - `name` (str, required)
  - `age` (int)
  - `position` (str)
  - `created_at` (datetime)

- Table: `shift`
  - `id` (int, PK)
  - `date` (date, required)
  - `shift_type` (enum/string: e.g., morning/afternoon/night)

- Table: `assignment`
  - `id` (int, PK)
  - `shift_id` (FK -> shift.id)
  - `staff_id` (FK -> staff.id)
  - Unique constraint on (`shift_id`, `staff_id`)


### API Endpoints (typical)
- Staff
  - `GET /staff` – list staff
  - `POST /staff` – create staff { name, age, position }
  - `DELETE /staff/{id}` – delete staff

- Shifts & Assignments
  - `GET /roster?start=YYYY-MM-DD&end=YYYY-MM-DD` – list assignments in range
  - `POST /assignments` – assign staff to a shift { date, shift_type, staff_id }
  - `DELETE /assignments/{id}` – unassign

- Statistics
  - `GET /stats/coverage?start=...&end=...` – per-day coverage counts
  - `GET /stats/staff-load?start=...&end=...` – assignments per staff

- Export
  - `GET /export/roster.csv?start=...&end=...` – CSV export of assignments

- Auto Scheduling
  - `POST /schedule/auto` – input { start, end, shift_types, min_per_shift } → generates assignments


### Scheduling Logic (baseline)
- Manual assignment: user picks a date, shift type, and staff.
- Automatic scheduling (simple heuristic):
  - Iterate dates and shift types; for each, choose the staff member with the lowest current assignment count who is not yet assigned on that date and meets constraints.
  - Ensure fairness by round‑robin distribution and balance total load across staff.


### Frontend Pages
- `StaffManagement.vue`: CRUD for staff list.
- `RosterDisplay.vue`: Calendar/table view of assignments; filter by date range; summary stats; actions to assign/unassign; export button; auto-schedule trigger.


### Testing
- Backend: pytest, httpx for API tests.
- Frontend: Vitest + Vue Test Utils.

Run backend tests:

```bash
cd backend
pip install -r requirements.txt
pytest -q
```

Run frontend tests:

```bash
cd frontend
npm install
npm run test
```
