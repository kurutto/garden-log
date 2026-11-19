from datetime import date
from pydantic import BaseModel
import uuid
import json

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import (
    create_engine,
    select,
)
from sqlalchemy.orm import (
    Session,
    sessionmaker,
)
from models import (
    Vegetable,
    WorkType,
    GardenRecord,
    FarmSVG,
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


class SVGDataSchema(BaseModel):
    viewBox: str
    elements: list[dict]


class FarmSchema(BaseModel):
    farmName: str
    svgData: SVGDataSchema


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    vegetables = db.scalars(select(Vegetable).order_by(Vegetable.name)).all()

    work_types = db.scalars(select(WorkType).order_by(WorkType.name)).all()

    farms = db.scalars(select(FarmSVG).order_by(FarmSVG.farm_name)).all()
    farm_data = [
        {
            "id": str(farm.id),
            "farm_name": farm.farm_name,
            "svg_data": farm.svg_data,
        }
        for farm in farms
    ]

    records = db.scalars(
        select(GardenRecord).order_by(
            GardenRecord.work_date.desc(), GardenRecord.id.desc()
        )
    ).all()

    # 野菜ごとに作業記録をまとめる
    grouped_records = []

    for vegetable in vegetables:
        vegetable_records = sorted(
            [record for record in records if record.vegetable_id == vegetable.id],
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
            harvest_totals[unit] = harvest_totals.get(unit, 0) + record.harvest_amount

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
            "farm": farm_data,
            "grouped_records": grouped_records,
        },
    )


# @app.get("/farm", response_class=HTMLResponse)
# def read_farm(request: Request):
#     return templates.TemplateResponse(
#         request=request,
#         name="farm.html",
#         context={
#             "title": "家庭菜園の記録 - 農場区画情報",
#         },
#     )


@app.post("/farm")
def create_farm(data: FarmSchema, db: Session = Depends(get_db)):
    farm_data = FarmSVG(farm_name=data.farmName, svg_data=data.svgData.model_dump())

    db.add(farm_data)
    db.commit()
    db.refresh(farm_data)

    return {"id": farm_data.id}


@app.post("/vegetables")
def create_vegetable(
    name: str = Form(...),
    farm_id: uuid.UUID = Form(...),
    area_id: uuid.UUID = Form(...),
    farm_svg: str = Form(...),
    db: Session = Depends(get_db),
):
    name = name.strip()
    farm_data = json.loads(farm_svg)
    svg_data = farm_data["svgData"]

    if not name or not farm_id or not area_id:
        raise HTTPException(
            status_code=400, detail="名前とファームとエリアは必須です。"
        )

    existing = db.scalar(select(Vegetable).where(Vegetable.name == name))

    if existing:
        existing.farm_id = farm_id
        existing.area_id = area_id
    else:
        db.add(Vegetable(name=name, farm_id=farm_id, area_id=area_id))

    farm = db.scalar(select(FarmSVG).where(FarmSVG.id == farm_id))
    farm.svg_data = svg_data

    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/work-types")
def create_work_type(
    name: str = Form(...),
    db: Session = Depends(get_db),
):
    name = name.strip()

    if name and db.scalar(select(WorkType).where(WorkType.name == name)) is None:
        db.add(WorkType(name=name))
        db.commit()

    return RedirectResponse(url="/", status_code=303)


@app.post("/records")
def create_record(
    work_date: date = Form(...),
    vegetable_id: uuid.UUID = Form(...),
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


@app.post("/vegetables/{vegetable_id}/delete")
def delete_vegetable(vegetable_id: uuid.UUID, db: Session = Depends(get_db)):
    vegetable = db.get(Vegetable, vegetable_id)
    if vegetable is None:
        raise HTTPException(status_code=400, detail="データがありません。")
    db.delete(vegetable)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/vegetables/{vegetable_id}/records")
async def update_vegetable(
    vegetable_id: uuid.UUID, request: Request, db: Session = Depends(get_db)
):
    form_data = await request.form()
    rids = form_data.getlist("record_id")
    for rid in rids:
        record = db.get(GardenRecord, int(rid))
        if record is None or record.vegetable_id != vegetable_id:
            raise HTTPException(status_code=400, detail="不正な記録が含まれています。")

        if f"work_date_{rid}" in form_data:
            record.work_date = date.fromisoformat(form_data[f"work_date_{rid}"])
        if f"memo_{rid}" in form_data:
            record.memo = form_data[f"memo_{rid}"].strip()
        if f"harvest_amount_{rid}" in form_data:
            record.harvest_amount = float(form_data[f"harvest_amount_{rid}"]) or None
        if f"harvest_unit_{rid}" in form_data:
            record.harvest_unit = form_data[f"harvest_unit_{rid}"] or None
    db.commit()
    return RedirectResponse(url="/", status_code=303)
