# Support Ticketing CRM API

This folder contains the FastAPI backend. The frontend will live in a separate
top-level folder.

## Local setup

1. Create a virtual environment and install dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and set `DATABASE_URL` to the Supabase
   PostgreSQL connection string. If it is omitted, the app uses a local SQLite
   database for quick development.

3. Start the API from this folder:

   ```powershell
   uvicorn app.main:app --reload
   ```

Interactive API documentation is available at `http://localhost:8000/docs`.

## API

- `POST /api/tickets` creates a ticket.
- `GET /api/tickets?status=Open&search=term` lists, filters, and searches.
- `GET /api/tickets/{ticket_id}` returns ticket details and notes.
- `PUT /api/tickets/{ticket_id}` updates status and appends one optional note.

The two database tables are `tickets` and `notes`, matching the assessment
specification. Tables are created automatically at application startup.
