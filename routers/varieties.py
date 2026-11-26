from fastapi import Depends, APIRouter, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
import crud

router = APIRouter()


@router.post("/varieties")
def create_variety(
    name: str = Form(...),
    db: Session = Depends(get_db),
):
    name = name.strip()
    crud.create_variety(name, db)

    return RedirectResponse(url="/", status_code=303)
