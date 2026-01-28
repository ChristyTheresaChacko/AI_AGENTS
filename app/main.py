from fastapi import FastAPI, HTTPException
import logging

from app.models import ProjectStatusUpdate
from app.scheduler_service import scheduler_service, send_csat_email
from dotenv import load_dotenv

load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CSAT Automation Service")

@app.on_event("startup")
async def startup():
    scheduler_service.start()

@app.on_event("shutdown")
async def shutdown():
    scheduler_service.shutdown()

@app.post("/projects/{project_id}/status")
async def update_project_status(project_id: str, payload: ProjectStatusUpdate):
    """Endpoint to notify the service that a project's status changed.

    Path parameter:
      - project_id: string provided by the caller (it's the project's id)

    Body (JSON): ProjectStatusUpdate -- includes status, customer_email, start_date
    """
    logger.info("Project %s status changed → %s", project_id, payload.status)

    try:
        # 1) Send immediate CSAT email
        send_csat_email(
            payload.customer_email,
            project_id,
            f"Milestone reached: {payload.status}"
        )

        # 2) Schedule recurring 6-month CSAT using project start date
        scheduler_service.schedule_6_month_csat(
            payload.customer_email,
            project_id,
            payload.start_date,
        )

        return {
            "message": "CSAT email sent & recurring scheduled",
            "project_id": project_id,
            "status": payload.status,
        }

    except Exception as e:
        # Log and return helpful error message so the client can see why
        logger.exception("Failed to process CSAT for project %s", project_id)
        # Return the exception message (safe because it should not contain secrets here)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health():
    return {"status": "CSAT Service Running"}
