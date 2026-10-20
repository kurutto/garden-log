
from datetime import date

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Date, Float, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# SQLite database
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


# Database model
class Base(DeclarativeBase):
    pass


class GardenRecord(Base):
    __tablename__ = "garden_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    work_date: Mapped[date] = mapped_column(Date, nullable=False)
    vegetable: Mapped[str] = mapped_column(String(100), nullable=False)
    work: Mapped[str] = mapped_column(String(100), nullable=False)
    memo: Mapped[str] = mapped_column(Text, default="", nullable=False)
    harvest_amount: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    harvest_unit: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )


# Create tables if they do not exist
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    statement = select(GardenRecord).order_by(
        GardenRecord.work_date.desc(),
        GardenRecord.id.desc(),
    )
    records = db.scalars(statement).all()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "家庭菜園の記録",
            "today": date.today().isoformat(),
            "records": records,
        },
    )


@app.post("/records")
def create_record(
    work_date: date = Form(...),
    vegetable: str = Form(...),
    work: str = Form(...),
    memo: str = Form(""),
    harvest_amount: float | None = Form(None),
    harvest_unit: str = Form(""),
    db: Session = Depends(get_db),
):
    record = GardenRecord(
        work_date=work_date,
        vegetable=vegetable.strip(),
        work=work.strip(),
        memo=memo.strip(),
        harvest_amount=harvest_amount,
        harvest_unit=harvest_unit.strip() or None,
    )

    db.add(record)
    db.commit()

    return RedirectResponse(url="/", status_code=303)
