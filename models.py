from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    String,
    func,
    true,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship
db = SQLAlchemy()

class Service(db.Model):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    completed_message: Mapped[str] = mapped_column(String(250))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="service")


class Ticket(db.Model):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    driver_name: Mapped[str] = mapped_column(String(120))
    service_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("services.id", ondelete="RESTRICT"),
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="Waiting",
        server_default="Waiting",
    )
    is_priority: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    called_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    no_show_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    service: Mapped["Service"] = relationship(back_populates="tickets")
    items: Mapped[list["TicketItem"]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('Waiting', 'Processing', 'Completed', 'No-Show', 'Left')",
            name="ck_tickets_status",
        ),
        CheckConstraint(
            """
            (status = 'Waiting'
                AND called_at IS NULL AND completed_at IS NULL
                AND no_show_at IS NULL AND left_at IS NULL)
            OR (status = 'Processing'
                AND called_at IS NOT NULL AND completed_at IS NULL
                AND no_show_at IS NULL AND left_at IS NULL)
            OR (status = 'Completed'
                AND called_at IS NOT NULL AND completed_at IS NOT NULL
                AND no_show_at IS NULL AND left_at IS NULL)
            OR (status = 'No-Show'
                AND called_at IS NULL AND completed_at IS NULL
                AND no_show_at IS NOT NULL AND left_at IS NULL)
            OR (status = 'Left'
                AND called_at IS NULL AND completed_at IS NULL
                AND no_show_at IS NULL AND left_at IS NOT NULL)
            """,
            name="tickets_status_timestamps_check",
        ),
    )


class TicketItem(db.Model):
    __tablename__ = "ticket_items"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    ticket_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tickets.id", ondelete="CASCADE"),
    )
    item_name: Mapped[str] = mapped_column(String(120))
    quantity: Mapped[int] = mapped_column(Integer)

    ticket: Mapped["Ticket"] = relationship(back_populates="items")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_ticket_items_quantity_positive"),
    )
