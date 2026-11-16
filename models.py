from datetime import date
from pathlib import Path
from pydantic import BaseModel
from sqlalchemy import JSON

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import (
    Date,
    Float,
    ForeignKey,
    String,
    Text,
    create_engine,
    inspect,
    select,
    text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)


class Base(DeclarativeBase):
    pass


class Vegetable(Base):
    __tablename__ = "vegetables"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    area: Mapped[str] = mapped_column(String(100), default="", nullable=False)

    records: Mapped[list["GardenRecord"]] = relationship(
        back_populates="vegetable_info", cascade="all, delete", passive_deletes=True
    )


class WorkType(Base):
    __tablename__ = "work_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)


class GardenRecord(Base):
    __tablename__ = "garden_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    work_date: Mapped[date] = mapped_column(Date, nullable=False)

    # 既存データとの互換性のため、従来の文字列カラムを残す
    vegetable: Mapped[str] = mapped_column(String(100), nullable=False)

    # 新しい野菜テーブルとの関連
    vegetable_id: Mapped[int | None] = mapped_column(
        ForeignKey("vegetables.id", ondelete="CASCADE"),
        nullable=True,
    )

    work: Mapped[str] = mapped_column(String(100), nullable=False)
    memo: Mapped[str] = mapped_column(Text, default="", nullable=False)
    harvest_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    harvest_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)

    vegetable_info: Mapped[Vegetable | None] = relationship(back_populates="records")


class FarmSVG(Base):
    __tablename__ = "farm_svg"

    id: Mapped[int] = mapped_column(primary_key=True)
    farm_name: Mapped[str] = mapped_column(Text, default="", nullable=False)
    svg_data: Mapped[dict] = mapped_column(JSON, nullable=False)

    # 新しい野菜テーブルとの関連
    vegetable_id: Mapped[int | None] = mapped_column(
        ForeignKey("vegetables.id", ondelete="CASCADE"),
        nullable=True,
    )
