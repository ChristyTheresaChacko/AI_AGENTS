from pydantic import BaseModel
from datetime import date


class ProjectStatusUpdate(BaseModel):
    status: str
    customer_email: str
    # ISO date for project start (YYYY-MM-DD). Scheduler will use this as the
    # baseline for 6-month (180-day) recurring emails.
    start_date: date
