from datetime import date
import uuid
from sqlalchemy import (
    Date,
    Float,
    ForeignKey,
    String,
    Text,
    JSON,
    Uuid,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class Vegetable(Base):
    __tablename__ = "vegetables"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    farm_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("farm_svg.id", ondelete="SET NULL"), nullable=True
    )
    area_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)

    records: Mapped[list["GardenRecord"]] = relationship(
        back_populates="vegetable_info", cascade="all, delete", passive_deletes=True
    )
    farm_svg: Mapped["FarmSVG | None"] = relationship(back_populates="vegetables")


class WorkType(Base):
    __tablename__ = "work_types"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)


class GardenRecord(Base):
    __tablename__ = "garden_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    work_date: Mapped[date] = mapped_column(Date, nullable=False)

    # 既存データとの互換性のため、従来の文字列カラムを残す
    vegetable: Mapped[str] = mapped_column(String(100), nullable=False)

    # 新しい野菜テーブルとの関連
    vegetable_id: Mapped[uuid.UUID | None] = mapped_column(
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

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    farm_name: Mapped[str] = mapped_column(Text, default="", nullable=False)
    svg_data: Mapped[dict] = mapped_column(JSON, nullable=False)

    vegetables: Mapped[list["Vegetable"]] = relationship(back_populates="farm_svg")
