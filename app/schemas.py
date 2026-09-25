"""Pydantic schemas used by the public API."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class TicketStatus(str, Enum):
    """The only statuses supported by the assessment specification."""

    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    CLOSED = "Closed"


class TicketCreate(BaseModel):
    """Fields required to create a ticket."""

    # Trim user input before applying min_length so whitespace-only values
    # are rejected instead of being stored as empty text.
    model_config = ConfigDict(str_strip_whitespace=True)

    customer_name: str = Field(min_length=1, max_length=120)
    customer_email: EmailStr
    subject: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)


class TicketCreateResponse(BaseModel):
    """Minimal response returned after creating a ticket."""

    ticket_id: str
    created_at: datetime


class TicketListItem(BaseModel):
    """Ticket fields needed by the list view."""

    model_config = ConfigDict(from_attributes=True)

    ticket_id: str
    customer_name: str
    subject: str
    status: TicketStatus
    created_at: datetime


class NoteResponse(BaseModel):
    """A serialized ticket note."""

    model_config = ConfigDict(from_attributes=True)

    note_text: str
    created_at: datetime


class TicketDetail(BaseModel):
    """Full ticket representation returned by the detail endpoint."""

    model_config = ConfigDict(from_attributes=True)

    ticket_id: str
    customer_name: str
    customer_email: EmailStr
    subject: str
    description: str
    status: TicketStatus
    notes: list[NoteResponse]


class TicketUpdate(BaseModel):
    """Fields that can be changed on a ticket."""

    status: TicketStatus
    notes: str | None = Field(default=None, max_length=5000)


class TicketUpdateResponse(BaseModel):
    """Confirmation returned after a ticket update."""

    success: bool
    updated_at: datetime
