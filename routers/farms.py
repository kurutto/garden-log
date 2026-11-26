from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from database import get_db
from schemas import FarmSchema
import crud

router = APIRouter()


@router.post("/farms")
def create_farm(data: FarmSchema, db: Session = Depends(get_db)):
    farmId = crud.create_farm(data, db)
    return {"id": farmId}
