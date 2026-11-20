import uuid
import json

from fastapi import Depends, APIRouter, Form, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
import crud

router = APIRouter()


@router.post("/vegetables")
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


@router.post("/vegetables/{vegetable_id}/delete")
def delete_vegetable(vegetable_id: uuid.UUID, db: Session = Depends(get_db)):
    crud.delete_vegetable(vegetable_id, db)
    return RedirectResponse(url="/", status_code=303)
