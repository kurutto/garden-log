from datetime import date

from fastapi import Depends, APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
import crud

router = APIRouter()

router.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
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
