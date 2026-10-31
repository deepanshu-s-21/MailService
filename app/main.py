import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse

from app.schemas import EmailRequest
from app.email_service import send_email, get_smtp_config_status
from app.db import (
    init_db,
    save_email,
    get_emails,
    get_email_by_id,
    delete_email,
    get_stats
)


app = FastAPI(
    title="Mail Service",
    description="Reusable service for sending emails with web dashboard and history",
    version="1.1.0"
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_HTML = STATIC_DIR / "index.html"

# Initialize DB immediately on module import
init_db()


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    """Serve the modern web UI dashboard."""
    if INDEX_HTML.exists():
        return HTMLResponse(content=INDEX_HTML.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Mail Service UI file not found</h1>", status_code=404)


@app.get("/ui", response_class=HTMLResponse)
def serve_dashboard_alias():
    """Alias for web UI dashboard."""
    return serve_dashboard()


@app.get("/health")
def health():
    return {
        "status": "UP",
        "service": "Mail Service"
    }


@app.get("/api/info")
def smtp_info():
    """Get non-sensitive SMTP configuration details for UI indicators."""
    return get_smtp_config_status()


@app.get("/api/stats")
def email_stats():
    """Return counts of total, sent, and failed emails."""
    return get_stats()


@app.get("/api/emails")
def list_sent_emails(
    search: Optional[str] = Query(None, description="Search term for recipient, subject or body"),
    status: Optional[str] = Query(None, description="Filter by status: SENT or FAILED"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0)
):
    """Retrieve history of sent emails with filtering and pagination."""
    return get_emails(search=search, status=status, limit=limit, offset=offset)


@app.get("/api/emails/{email_id}")
def get_single_email(email_id: int):
    """Get single email record by ID."""
    email = get_email_by_id(email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email record not found")
    return email


@app.delete("/api/emails/{email_id}")
def delete_single_email(email_id: int):
    """Delete an email record from history."""
    deleted = delete_email(email_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Email record not found")
    return {"success": True, "message": f"Email #{email_id} deleted successfully"}


@app.post("/api/email/send")
def send_email_endpoint(request: EmailRequest):
    """
    Send an email and log the result into the database.
    Works for both UI compose submissions and programmatic API calls.
    """
    try:
        send_email(
            to=request.to,
            subject=request.subject,
            body=request.body
        )

        email_id = save_email(
            recipient=str(request.to),
            subject=request.subject,
            body=request.body,
            status="SENT"
        )

        return {
            "success": True,
            "message": "Email sent successfully",
            "id": email_id
        }

    except Exception as e:
        error_msg = str(e)
        print("EMAIL ERROR:", repr(e))

        email_id = None
        try:
            email_id = save_email(
                recipient=str(request.to),
                subject=request.subject,
                body=request.body,
                status="FAILED",
                error_message=error_msg
            )
        except Exception as db_err:
            print("DB SAVE ERROR:", repr(db_err))

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Failed to send email: {error_msg}",
                "detail": error_msg,
                "id": email_id
            }
        )
