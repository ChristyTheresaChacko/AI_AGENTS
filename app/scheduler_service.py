from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta, date
from typing import Union
from app.email_service import send_email
import logging

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self):
        self.scheduler.start()

    def shutdown(self):
        self.scheduler.shutdown()

    def schedule_6_month_csat(self, email: str, project_id: str, start_date: Union[datetime, date, str]):
        """Schedule a recurring CSAT email every 180 days starting at
        (project start_date + 180 days).

        start_date may be a datetime or an ISO date string (YYYY-MM-DD).
        """
        job_id = f"csat_{project_id}"

        if self.scheduler.get_job(job_id):
            logger.info("CSAT job already exists for %s", project_id)
            return

        # Normalize start_date to a datetime
        if isinstance(start_date, str):
            try:
                start_dt = datetime.fromisoformat(start_date)
            except Exception:
                # try parsing as date only or fallback to midnight
                start_dt = datetime.fromisoformat(start_date + "T00:00:00")
        elif isinstance(start_date, date) and not isinstance(start_date, datetime):
            # convert date to datetime at midnight
            start_dt = datetime.combine(start_date, datetime.min.time())
        elif isinstance(start_date, datetime):
            start_dt = start_date
        else:
            # fallback: use current time
            start_dt = datetime.now()

        first_run = start_dt + timedelta(days=180)

        self.scheduler.add_job(
            send_csat_email,
            trigger="interval",
            days=180,
            start_date=first_run,
            args=[email, project_id, "6-Month CSAT"],
            id=job_id
        )

def send_csat_email(email: str, project_id: str, context: str):
    subject = f"CSAT Feedback – Project {project_id}"
    body = f"""
Hello,

Please share your feedback for Project {project_id}.
Context: {context}

Thank you,
CSAT Team
"""
    try:
        ok = send_email(email, subject, body)
        if ok:
            logger.info("CSAT email sent (%s) to %s", context, email)
        else:
            logger.warning("CSAT email could not be sent via SMTP; saved to sent_emails.log for %s", email)
    except Exception:
        # send_email should not raise after our changes, but guard anyway
        logger.exception("Unexpected error while sending CSAT email to %s", email)

scheduler_service = SchedulerService()
