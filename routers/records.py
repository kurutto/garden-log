from datetime import date
import uuid

from fastapi import Depends, APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
import crud

router = APIRouter()


@router.post("/records")
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


@router.post("/vegetables/{vegetable_id}/records")
async def update_vegetable(
    vegetable_id: uuid.UUID, request: Request, db: Session = Depends(get_db)
):
    form_data = await request.form()
    await crud.update_vegetable(vegetable_id, form_data, db)
    return RedirectResponse(url="/", status_code=303)
