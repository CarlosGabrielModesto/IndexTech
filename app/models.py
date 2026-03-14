"""
Modelos do domínio — tabelas do banco de dados.
Usa SQLAlchemy puro (compatível com Python 3.14).
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Boolean, Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class Person(Base):
    __tablename__ = "person"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, index=True)
    birthdate: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    neighborhood: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ubs: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    cep: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    raca_cor: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    consent_optout: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class Invitation(Base):
    __tablename__ = "invitation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("person.id"), index=True)
    status: Mapped[str] = mapped_column(String, default="pending", index=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    response: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class Appointment(Base):
    __tablename__ = "appointment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    person_id: Mapped[int] = mapped_column(Integer, ForeignKey("person.id"), index=True)
    when: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    place: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="scheduled")
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)