import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date
from schemas import SVGDataSchema, FarmSchema
from models import (
    Vegetable,
    WorkType,
    GardenRecord,
    FarmSVG,
)
from fastapi import HTTPException, Request


def get_vegetables(db: Session):
    return db.scalars(select(Vegetable).order_by(Vegetable.name)).all()


def get_vegetable(vegetable_id: uuid.UUID, db: Session):
    return db.get(Vegetable, vegetable_id)


def get_work_types(db: Session):
    return db.scalars(select(WorkType).order_by(WorkType.name)).all()


def get_work_type(work_name: str, db: Session):
    return db.scalar(select(WorkType).where(WorkType.name == work_name))


def get_farms(db: Session):
    return db.scalars(select(FarmSVG).order_by(FarmSVG.farm_name)).all()


def get_records(db: Session):
    return db.scalars(
        select(GardenRecord).order_by(
            GardenRecord.work_date.desc(), GardenRecord.id.desc()
        )
    ).all()


def get_record(record_id: uuid.UUID, db: Session):
    return db.get(GardenRecord, record_id)


def create_vegetable(
    name: str,
    farm_id: uuid.UUID,
    area_id: uuid.UUID,
    svg_data: SVGDataSchema,
    db: Session,
):
    existing = db.scalar(select(Vegetable).where(Vegetable.name == name))

    if existing:
        existing.farm_id = farm_id
        existing.area_id = area_id
    else:
        db.add(Vegetable(name=name, farm_id=farm_id, area_id=area_id))

    farm = db.scalar(select(FarmSVG).where(FarmSVG.id == farm_id))
    if farm is None:
        raise ValueError("ファームIDが一致しません")
    farm.svg_data = svg_data

    db.commit()


def create_work_type(name: str, db: Session):
    if name and db.scalar(select(WorkType).where(WorkType.name == name)) is None:
        db.add(WorkType(name=name))
        db.commit()


def create_farm(data: FarmSchema, db: Session):
    farm_data = FarmSVG(farm_name=data.farmName, svg_data=data.svgData.model_dump())

    db.add(farm_data)
    db.commit()
    db.refresh(farm_data)

    return {"id": farm_data.id}


def create_record(
    work_date: date,
    vegetable: str,
    vegetable_id: uuid.UUID,
    work_name: str,
    memo: str,
    harvest_amount: float | None,
    harvest_unit: str | None,
    db: Session,
):
    db.add(
        GardenRecord(
            work_date=work_date,
            vegetable=vegetable.name,
            vegetable_id=vegetable_id,
            work_name=work_name,
            memo=memo,
            harvest_amount=harvest_amount,
            harvest_unit=harvest_unit,
        )
    )
    db.commit()


def update_vegetable(vegetable_id: uuid.UUID, form_data, db: Session):
    rids = form_data.getlist("record_id")
    for rid in rids:
        record = get_record(uuid.UUID(rid), db)
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


def delete_vegetable(vegetable_id: uuid.UUID, db: Session):
    vegetable = get_vegetable(Vegetable, vegetable_id)
    if vegetable is None:
        raise HTTPException(status_code=404, detail="データがありません。")
    db.delete(vegetable)
    db.commit()
