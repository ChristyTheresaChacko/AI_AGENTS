CSAT Automation Service

This small FastAPI app sends an immediate CSAT email when a project status changes and schedules recurring 6-month CSAT emails from the project's start date.

Quick start

1. Install dependencies (prefer a virtualenv):

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with SMTP settings (if you want real emails):

```ini
# Use MAIL_BACKEND=smtp to force SMTP even if vars missing
MAIL_BACKEND=auto
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your_username
SMTP_PASSWORD=your_password
SMTP_FROM_EMAIL=no-reply@example.com
```

If you don't provide SMTP settings, the app will fall back to writing emails to `sent_emails.log` (useful for dev).

3. Run the app (recommended):

```bash
uvicorn app.main:app --reload
```

4. Example request (replace values):

```bash
curl -X POST "http://127.0.0.1:8000/projects/PROJECT123/status" -H "Content-Type: application/json" -d '{"status":"DELIVERED","customer_email":"client@example.com","start_date":"2025-12-30"}'
```

Notes
- `project_id` is provided by the caller as the path parameter. It's the identifier for the project and used to create unique scheduled job ids.
- By default, the scheduler will schedule the first 6-month CSAT at `start_date + 180 days` and then repeat every 180 days.
- For production, run with a process manager and set real SMTP credentials.

Files changed/added
- `app/models.py` — added `start_date: date` field.
- `app/scheduler_service.py` — robust date handling and uses `app.email_service`.
- `app/email_service.py` — supports SMTP and console/file fallback.
- `app/main.py` — improved error messages and package imports.
- `requirements.txt`, `README.md` added.

If you'd like, I can:
- Add unit tests (pytest) for the scheduler date calculation and endpoint behavior.
- Replace `@app.on_event` lifecycle with FastAPI Lifespan manager.
- Configure a small local testing SMTP server and show a live email send example.
