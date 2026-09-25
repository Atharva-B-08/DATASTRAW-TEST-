"""FastAPI application for the Support Ticketing CRM."""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Note, Ticket
from .schemas import (
    TicketCreate,
    TicketCreateResponse,
    TicketDetail,
    TicketListItem,
    TicketStatus,
    TicketUpdate,
    TicketUpdateResponse,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create tables on startup for the assessment-sized application."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Support Ticketing CRM API",
    description="REST API for managing customer support tickets.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_ticket_or_404(ticket_id: str, db: Session) -> Ticket:
    """Find a ticket by its public ID or raise the API's standard 404."""
    ticket = db.scalar(select(Ticket).where(Ticket.ticket_id == ticket_id))
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.post(
    "/api/tickets",
    response_model=TicketCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    """Create a ticket and generate its human-readable public ID."""
    last_ticket = db.scalar(select(Ticket).order_by(Ticket.id.desc()).limit(1))
    next_number = (last_ticket.id + 1) if last_ticket else 1
    ticket = Ticket(
        ticket_id=f"TKT-{next_number:03d}",
        customer_name=payload.customer_name.strip(),
        customer_email=str(payload.customer_email),
        subject=payload.subject.strip(),
        description=payload.description.strip(),
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


@app.get("/api/tickets", response_model=list[TicketListItem])
def list_tickets(
    status_filter: TicketStatus | None = Query(default=None, alias="status"),
    search: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
):
    """List tickets, optionally filtered by exact status and broad text search."""
    statement = select(Ticket).order_by(Ticket.created_at.desc())
    if status_filter:
        statement = statement.where(Ticket.status == status_filter.value)
    if search:
        search_term = f"%{search.strip()}%"
        statement = statement.where(
            or_(
                Ticket.ticket_id.ilike(search_term),
                Ticket.customer_name.ilike(search_term),
                Ticket.customer_email.ilike(search_term),
                Ticket.subject.ilike(search_term),
                Ticket.description.ilike(search_term),
            )
        )
    return list(db.scalars(statement).all())


@app.get("/api/tickets/{ticket_id}", response_model=TicketDetail)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Return one ticket with its notes."""
    return _get_ticket_or_404(ticket_id, db)


@app.put("/api/tickets/{ticket_id}", response_model=TicketUpdateResponse)
def update_ticket(
    ticket_id: str, payload: TicketUpdate, db: Session = Depends(get_db)
):
    """Update status and append one optional collaboration note."""
    ticket = _get_ticket_or_404(ticket_id, db)
    ticket.status = payload.status.value
    if payload.notes and payload.notes.strip():
        ticket.notes.append(Note(note_text=payload.notes.strip()))
    db.commit()
    db.refresh(ticket)
    return TicketUpdateResponse(success=True, updated_at=ticket.updated_at)


@app.get("/health")
def health_check():
    """Simple deployment health check for Railway."""
    return {"status": "ok"}
