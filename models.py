from database import Base
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from sqlalchemy import (
    Date,
    Float,
    ForeignKey,
    String,
    Text,
    JSON,
    Uuid,
)
from datetime import date
import uuid


class Cultivations(Base):
    __tablename__ = "cultivations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    variety_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("varieties.id", ondelete="SET NULL"), nullable=True
    )
    farm_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("farms.id", ondelete="SET NULL"), nullable=True
    )
    area_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    area_size: Mapped[Float | None] = mapped_column(Float, nullable=True)

    records: Mapped[list["Records"]] = relationship(
        back_populates="cultivation", cascade="all, delete", passive_deletes=True
    )
    variety: Mapped["Varieties | None"] = relationship(back_populates="cultivations")
    farm: Mapped["Farms | None"] = relationship(back_populates="cultivations")


class Varieties(Base):
    __tablename__ = "varieties"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    cultivations: Mapped[list["Cultivations"]] = relationship(
        back_populates="variety",
        passive_deletes=True,
    )


class WorkTypes(Base):
    __tablename__ = "work_types"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    records: Mapped[list["Records"]] = relationship(
        back_populates="work_type",
        passive_deletes=True,
    )


class Farms(Base):
    __tablename__ = "farms"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, default="", nullable=False)
    svg_data: Mapped[dict] = mapped_column(JSON, nullable=False)

    cultivations: Mapped[list["Cultivations"]] = relationship(
        back_populates="farm",
        passive_deletes=True,
    )


class Records(Base):
    __tablename__ = "records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    cultivation_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("cultivations.id", ondelete="CASCADE"),
        nullable=True,
    )
    work_type_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("work_types.id", ondelete="SET NULL"), nullable=True
    )
    memo: Mapped[str | None] = mapped_column(Text, default="", nullable=True)
    harvest_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    harvest_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)

    cultivation: Mapped[Cultivations | None] = relationship(back_populates="records")
    work_type: Mapped["WorkTypes"] = relationship(back_populates="records")
