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
    date: date = Form(...),
    cultivation_id: uuid.UUID = Form(...),
    work_type_id: uuid.UUID = Form(...),
    memo: str = Form(""),
    amount: float | None = Form(None),
    unit: str | None = Form(None),
    db: Session = Depends(get_db),
):
    cultivation = crud.get_cultivation(cultivation_id, db)

    if cultivation is None:
        raise HTTPException(status_code=400, detail="野菜を選択してください。")

    if not work_type_id:
        raise HTTPException(status_code=400, detail="作業内容は必須です。")

    if amount is not None and amount < 0:
        raise HTTPException(status_code=400, detail="数量は0以上にしてください。")

    crud.create_record(
        date,
        cultivation_id,
        work_type_id,
        memo,
        amount,
        unit,
        db,
    )

    return RedirectResponse(url="/", status_code=303)


@router.post("/cultivations/{cultivation_id}/records")
async def update_cultivation(
    cultivation_id: uuid.UUID, request: Request, db: Session = Depends(get_db)
):
    form_data = await request.form()
    await crud.update_cultivation(cultivation_id, form_data, db)
    return RedirectResponse(url="/", status_code=303)
