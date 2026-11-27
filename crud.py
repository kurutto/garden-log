import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date
from schemas import SVGDataSchema, FarmSchema
from models import (
    Cultivations,
    WorkTypes,
    Varieties,
    Records,
    Farms,
)
from fastapi import HTTPException, Request


def get_cultivations(db: Session):
    return db.scalars(select(Cultivations).order_by(Cultivations.name)).all()


def get_cultivation(cultivation_id: uuid.UUID, db: Session):
    return db.get(Cultivations, cultivation_id)


def get_work_types(db: Session):
    return db.scalars(select(WorkTypes).order_by(WorkTypes.name)).all()


def get_varieties(db: Session):
    return db.scalars(select(Varieties).order_by(Varieties.name)).all()


# def get_work_type(work_name: str, db: Session):
#     return db.scalar(select(WorkTypes).where(WorkTypes.name == work_name))


def get_farms(db: Session):
    return db.scalars(select(Farms).order_by(Farms.name)).all()


def get_records(db: Session):
    return db.scalars(
        select(Records).order_by(Records.date.desc(), Records.id.desc())
    ).all()


def get_record(record_id: uuid.UUID, db: Session):
    return db.get(Records, record_id)


def create_cultivation(
    name: str,
    variety_id: uuid.UUID,
    farm_id: uuid.UUID,
    area_id: uuid.UUID,
    svg_data: SVGDataSchema,
    area_size: float,
    db: Session,
):
    existing = db.scalar(select(Cultivations).where(Cultivations.name == name))

    if existing:
        existing.farm_id = farm_id
        existing.area_id = area_id
    else:
        db.add(
            Cultivations(
                name=name,
                variety_id=variety_id,
                farm_id=farm_id,
                area_id=area_id,
                area_size=area_size,
            )
        )

    farm = db.scalar(select(Farms).where(Farms.id == farm_id))
    if farm is None:
        raise ValueError("ファームIDが一致しません")
    farm.svg_data = svg_data

    db.commit()


def create_work_type(name: str, db: Session):
    if name and db.scalar(select(WorkTypes).where(WorkTypes.name == name)) is None:
        db.add(WorkTypes(name=name))
        db.commit()


def create_variety(name: str, db: Session):
    if name and db.scalar(select(Varieties).where(Varieties.name == name)) is None:
        db.add(Varieties(name=name))
        db.commit()


def create_farm(data: FarmSchema, db: Session):
    farm_data = Farms(name=data.name, svg_data=data.svgData.model_dump())

    db.add(farm_data)
    db.commit()
    db.refresh(farm_data)

    return {"id": farm_data.id}


def create_record(
    date: date,
    cultivation_id: uuid.UUID,
    work_type_id: str,
    memo: str,
    amount: float | None,
    unit: str | None,
    db: Session,
):
    db.add(
        Records(
            date=date,
            cultivation_id=cultivation_id,
            work_type_id=work_type_id,
            memo=memo,
            amount=amount,
            unit=unit,
        )
    )
    db.commit()


def update_cultivation(cultivation_id: uuid.UUID, form_data, db: Session):
    rids = form_data.getlist("record_id")
    for rid in rids:
        record = get_record(uuid.UUID(rid), db)
        if record is None or record.cultivation_id != cultivation_id:
            raise HTTPException(status_code=400, detail="不正な記録が含まれています。")

        if f"date_{rid}" in form_data:
            record.date = date.fromisoformat(form_data[f"date_{rid}"])
        if f"memo_{rid}" in form_data:
            record.memo = form_data[f"memo_{rid}"].strip()
        if f"amount_{rid}" in form_data:
            record.amount = float(form_data[f"amount_{rid}"]) or None
        if f"unit_{rid}" in form_data:
            record.unit = form_data[f"unit_{rid}"] or None
    db.commit()


def delete_cultivation(Cultivation_id: uuid.UUID, db: Session):
    cultivation = get_cultivation(Cultivations, Cultivation_id)
    if cultivation is None:
        raise HTTPException(status_code=404, detail="データがありません。")
    db.delete(cultivation)
    db.commit()
