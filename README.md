# Mail Service ✉️

A fast, reusable email dispatching service built with FastAPI, complete with an interactive Web UI dashboard, email history logger, and SMTP integration.

---

## ✨ Features

- **Web Dashboard**: Modern, responsive UI served directly at `http://localhost:8000/`
- **Compose & Send Email**: Enter recipient address (`to`), subject, and email body with real-time HTML preview.
- **Sent Mail History**: Tracks and logs all emails sent through both the UI and the API (`/api/email/send`), including delivery status and timestamps.
- **Delivery Analytics**: Real-time stats showing total emails, successful deliveries, failed attempts, and success rate.
- **Email Detail Viewer**: Inspect the full body, timestamps, recipient info, and failure trace for any email.
- **One-Click Resend / Reuse**: Quick action to load past emails back into the compose form.
- **Quick Templates**: One-click templates for Welcome, Alert, and Receipt emails.
- **Zero Extra Dependencies**: Uses SQLite (`sqlite3` standard library) for local persistent history.

---

## 🚀 Getting Started

### 1. Environment Configuration

Ensure your `.env` file has the appropriate SMTP settings:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME="Your Company or Name"
```

### 2. Start the Server

Activate your virtual environment and start the Uvicorn development server:

```powershell
# Windows
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### 3. Open the Web UI

Open your browser and navigate to:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Web UI Dashboard |
| `GET` | `/health` | Health check endpoint |
| `POST` | `/api/email/send` | Send an email (`{"to": "...", "subject": "...", "body": "..."}`) |
| `GET` | `/api/emails` | Fetch sent emails history (supports `?search=...&status=SENT/FAILED`) |
| `GET` | `/api/emails/{id}` | Get details of a single email |
| `DELETE` | `/api/emails/{id}` | Delete an email record from history |
| `GET` | `/api/stats` | Delivery analytics & stats |
| `GET` | `/api/info` | SMTP configuration status |
| `GET` | `/docs` | Interactive Swagger API documentation |
