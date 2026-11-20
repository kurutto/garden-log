from datetime import date
import uuid
import json

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal
from schemas import FarmSchema
import crud

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    vegetables = crud.get_vegetables(db)
    work_types = crud.get_work_types(db)
    farms = crud.get_farms(db)
    records = crud.get_records(db)

    farm_data = [
        {
            "id": str(farm.id),
            "farm_name": farm.farm_name,
            "svg_data": farm.svg_data,
        }
        for farm in farms
    ]

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
            if record.work_name != "収穫" or record.harvest_amount is None:
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
            "farms": farm_data,
            "grouped_records": grouped_records,
        },
    )


@app.post("/farm")
def create_farm(data: FarmSchema, db: Session = Depends(get_db)):
    farmId = crud.create_farm(data, db)
    return {"id": farmId}


@app.post("/vegetables")
def create_vegetable(
    name: str = Form(...),
    farm_id: uuid.UUID = Form(...),
    area_id: uuid.UUID = Form(...),
    farm_svg: str = Form(...),
    db: Session = Depends(get_db),
):
    name = name.strip()
    farm_svg_data = json.loads(
        farm_svg
    )  # jsonにするとdictになるためfarm_svg_data["svgData"]のように[]書きになる
    svg_data = farm_svg_data["svgData"]

    if not name:
        raise HTTPException(status_code=400, detail="名前は必須です。")
    if not farm_id or not area_id:
        raise HTTPException(status_code=400, detail="ファームとエリアは必須です。")
    try:
        crud.create_vegetable(name, farm_id, area_id, svg_data, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return RedirectResponse(url="/", status_code=303)


@app.post("/work-types")
def create_work_type(
    name: str = Form(...),
    db: Session = Depends(get_db),
):
    name = name.strip()
    crud.create_work_type(name, db)

    return RedirectResponse(url="/", status_code=303)


@app.post("/records")
def create_record(
    work_date: date = Form(...),
    vegetable_id: uuid.UUID = Form(...),
    work_name: str = Form(...),
    memo: str = Form(""),
    harvest_amount: float | None = Form(None),
    harvest_unit: str = Form(""),
    db: Session = Depends(get_db),
):
    vegetable = crud.get_vegetable(vegetable_id, db)

    if vegetable is None:
        raise HTTPException(status_code=400, detail="野菜を選択してください。")

    if not work_name:
        raise HTTPException(status_code=400, detail="作業内容は必須です。")

    if harvest_amount is not None and harvest_amount < 0:
        raise HTTPException(status_code=400, detail="数量は0以上にしてください。")

    if work_name == "収穫" and harvest_amount is None:
        raise HTTPException(
            status_code=400,
            detail="収穫を記録する場合は数量を入力してください。",
        )

    crud.create_record(
        work_date,
        vegetable,
        vegetable_id,
        work_name,
        memo,
        harvest_amount,
        harvest_unit,
        db,
    )

    return RedirectResponse(url="/", status_code=303)


@app.post("/vegetables/{vegetable_id}/delete")
def delete_vegetable(vegetable_id: uuid.UUID, db: Session = Depends(get_db)):
    crud.delete_vegetable(vegetable_id, db)
    return RedirectResponse(url="/", status_code=303)


@app.post("/vegetables/{vegetable_id}/records")
async def update_vegetable(
    vegetable_id: uuid.UUID, request: Request, db: Session = Depends(get_db)
):
    await crud.update_vegetable(vegetable_id, request, db)
    return RedirectResponse(url="/", status_code=303)
