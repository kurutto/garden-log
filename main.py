
from datetime import date
from pathlib import Path

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

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DATABASE_URL = "sqlite:///./garden_log.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


class Vegetable(Base):
    __tablename__ = "vegetables"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    area: Mapped[str] = mapped_column(String(100), default="", nullable=False)

    records: Mapped[list["GardenRecord"]] = relationship(
        back_populates="vegetable_info"
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
        ForeignKey("vegetables.id"),
        nullable=True,
    )

    work: Mapped[str] = mapped_column(String(100), nullable=False)
    memo: Mapped[str] = mapped_column(Text, default="", nullable=False)
    harvest_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    harvest_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)

    vegetable_info: Mapped[Vegetable | None] = relationship(
        back_populates="records"
    )


def migrate_database():
    """既存の作業記録を残しながら、新しいテーブル構成へ移行する。"""
    Base.metadata.create_all(bind=engine)

    columns = {
        column["name"]
        for column in inspect(engine).get_columns("garden_records")
    }

    if "vegetable_id" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE garden_records "
                    "ADD COLUMN vegetable_id INTEGER "
                    "REFERENCES vegetables(id)"
                )
            )

    with SessionLocal() as db:
        records = db.scalars(select(GardenRecord)).all()

        for record in records:
            name = record.vegetable.strip()
            if not name:
                continue

            vegetable = db.scalar(
                select(Vegetable).where(Vegetable.name == name)
            )

            if vegetable is None:
                vegetable = Vegetable(name=name, area="")
                db.add(vegetable)
                db.flush()

            if record.vegetable_id is None:
                record.vegetable_id = vegetable.id

            work_name = record.work.strip()
            if work_name and db.scalar(
                select(WorkType).where(WorkType.name == work_name)
            ) is None:
                db.add(WorkType(name=work_name))

        db.commit()


migrate_database()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    vegetables = db.scalars(
        select(Vegetable).order_by(Vegetable.name)
    ).all()

    work_types = db.scalars(
        select(WorkType).order_by(WorkType.name)
    ).all()

    records = db.scalars(
        select(GardenRecord)
        .order_by(GardenRecord.work_date.desc(), GardenRecord.id.desc())
    ).all()

    # 野菜ごとに作業記録をまとめる
    grouped_records = []

    for vegetable in vegetables:
        vegetable_records = sorted(
    [
        record
        for record in records
        if record.vegetable_id == vegetable.id
    ],
    key=lambda record: (record.work_date, record.id),
)

        if not vegetable_records:
            continue

        # 単位ごとに収穫量を合計する
        harvest_totals = {}

        for record in vegetable_records:
            if record.work != "収穫" or record.harvest_amount is None:
                continue

            unit = record.harvest_unit or "単位なし"
            harvest_totals[unit] = (
                harvest_totals.get(unit, 0) + record.harvest_amount
            )

        grouped_records.append(
            {
                "vegetable": vegetable,
                "records": vegetable_records,
                "harvest_totals": harvest_totals,
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "家庭菜園の記録",
            "today": date.today().isoformat(),
            "vegetables": vegetables,
            "work_types": work_types,
            "grouped_records": grouped_records,
        },
    )


@app.post("/vegetables")
def create_vegetable(
    name: str = Form(...),
    area: str = Form(...),
    db: Session = Depends(get_db),
):
    name = name.strip()
    area = area.strip()

    if not name or not area:
        raise HTTPException(status_code=400, detail="名前とエリアは必須です。")

    existing = db.scalar(
        select(Vegetable).where(Vegetable.name == name)
    )

    if existing:
        existing.area = area
    else:
        db.add(Vegetable(name=name, area=area))

    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/work-types")
def create_work_type(
    name: str = Form(...),
    db: Session = Depends(get_db),
):
    name = name.strip()

    if name and db.scalar(
        select(WorkType).where(WorkType.name == name)
    ) is None:
        db.add(WorkType(name=name))
        db.commit()

    return RedirectResponse(url="/", status_code=303)


@app.post("/records")
def create_record(
    work_date: date = Form(...),
    vegetable_id: int = Form(...),
    work: str = Form(...),
    memo: str = Form(""),
    harvest_amount: float | None = Form(None),
    harvest_unit: str = Form(""),
    db: Session = Depends(get_db),
):
    vegetable = db.get(Vegetable, vegetable_id)

    if vegetable is None:
        raise HTTPException(status_code=400, detail="野菜を選択してください。")

    work = work.strip()
    if not work:
        raise HTTPException(status_code=400, detail="作業内容は必須です。")

    if harvest_amount is not None and harvest_amount < 0:
        raise HTTPException(status_code=400, detail="数量は0以上にしてください。")

    # 新しい作業内容が入力された場合にも登録する
    if db.scalar(select(WorkType).where(WorkType.name == work)) is None:
        db.add(WorkType(name=work))

    if work == "収穫" and harvest_amount is None:
        raise HTTPException(
            status_code=400,
            detail="収穫を記録する場合は数量を入力してください。",
        )

    record = GardenRecord(
        work_date=work_date,
        vegetable=vegetable.name,
        vegetable_id=vegetable.id,
        work=work,
        memo=memo.strip(),
        harvest_amount=harvest_amount,
        harvest_unit=harvest_unit.strip() or None,
    )

    db.add(record)
    db.commit()

    return RedirectResponse(url="/", status_code=303)
