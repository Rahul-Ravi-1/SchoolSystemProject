# School System API

A minimal FastAPI + SQLite backend to manage students, teachers, courses, sections, and enrollments.

## Quickstart (Windows PowerShell)

```powershell
cd "$PSScriptRoot"

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

# Run the API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API Docs: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Data model (MVP)
- Student(first_name, last_name, email)
- Teacher(first_name, last_name, email, subject)
- Course(title, description)
- Section(name, capacity, course_id, teacher_id)
- Enrollment(student_id, section_id, grade?)

Notes:
- Subjects: Math, English, Social Sciences, PE
- Sections are specific offerings of a course taught by a single teacher

## Seed the database
This will create 4 courses (subjects), 20 teachers (5 per subject), and 3 sections per teacher (60 total).

```powershell
# Ensure the app has created tables by starting the API at least once, or call init on import
python -c "from app.database import init_db; init_db(); from app.seed import seed; seed(); print('Seed complete')"
```

## Endpoints
- Students: `GET/POST/GET{id}` at `/students`
- Teachers: `GET/POST/GET{id}` at `/teachers`
- Courses: `GET/POST/GET{id}` at `/courses`
- Sections: `GET/POST/GET{id}/PATCH{id}/DELETE{id}` at `/sections`
- Enrollments:
  - Enroll: `POST /enrollments?student_id=..&section_id=..`
  - Unenroll: `DELETE /enrollments/{id}`
  - List a student's sections: `GET /enrollments/student/{student_id}`
  - List a section's students: `GET /enrollments/section/{section_id}`

## Next steps
- Add update/delete to students/teachers/courses
- Add validation (unique emails, capacity limits)
- Add filters (teachers by subject)
