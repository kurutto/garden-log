import uuid
from datetime import date, timedelta

from sqlalchemy import select, func

from database import SessionLocal
from models import (
    Cultivations,
    WorkTypes,
    Varieties,
    Records,
    Farms,
)

# ----------------------------------------
# UUID
# ----------------------------------------


def make_id(name: str) -> uuid.UUID:
    """同じ名前から常に同じUUIDを生成する"""
    return uuid.uuid5(uuid.NAMESPACE_URL, f"garden-log/{name}")


# ----------------------------------------
# マスターデータ
# ----------------------------------------

WORK_TYPE_NAMES = [
    "播種",
    "間引き",
    "収穫（数量）",
    "収穫（重量）",
    "追肥",
    "水やり",
]

VARIETY_NAMES = [
    "青首総太り",
    "耐病総太り",
    "向陽二号",
    "金系201号",
    "楽天",
]


# ----------------------------------------
# 品種ごとの栽培条件
# ----------------------------------------

CROP_SETTINGS = {
    "青首総太り": {
        "crop": "daikon",
        "sow_dates": ["2026-09-01", "2026-09-10", "2026-09-20"],
        "harvest_days": 65,
        "base_yield": 20.0,
        "quantity_unit": "本",
        "base_count": 35,
    },
    "耐病総太り": {
        "crop": "daikon",
        "sow_dates": ["2026-09-03", "2026-09-13", "2026-09-23"],
        "harvest_days": 65,
        "base_yield": 22.0,
        "quantity_unit": "本",
        "base_count": 38,
    },
    "向陽二号": {
        "crop": "carrot",
        "sow_dates": ["2026-07-15", "2026-07-25", "2026-08-05"],
        "harvest_days": 100,
        "base_yield": 12.0,
        "quantity_unit": "本",
        "base_count": 60,
    },
    "金系201号": {
        "crop": "cabbage",
        "sow_dates": ["2026-07-10", "2026-07-20", "2026-07-30"],
        "harvest_days": 110,
        "base_yield": 25.0,
        "quantity_unit": "玉",
        "base_count": 25,
    },
    "楽天": {
        "crop": "komatsuna",
        "sow_dates": ["2026-09-10", "2026-09-20", "2026-10-01"],
        "harvest_days": 35,
        "base_yield": 8.0,
        "quantity_unit": "束",
        "base_count": 40,
    },
}


# ----------------------------------------
# データ登録
# ----------------------------------------


def seed():

    with SessionLocal() as db:

        try:
            # --------------------------------
            # 既存データの確認
            # --------------------------------

            tables = [
                Records,
                Cultivations,
                Varieties,
                WorkTypes,
                Farms,
            ]

            for table in tables:
                count = db.scalar(select(func.count()).select_from(table))

                if count:
                    raise RuntimeError(
                        f"{table.__tablename__} に既存データがあります。"
                        "データを確認してから実行してください。"
                    )

            # --------------------------------
            # WorkTypes
            # --------------------------------

            work_types = {
                name: WorkTypes(
                    id=make_id(f"work-type/{name}"),
                    name=name,
                )
                for name in WORK_TYPE_NAMES
            }

            db.add_all(work_types.values())

            # --------------------------------
            # Varieties
            # --------------------------------

            varieties = {
                name: Varieties(
                    id=make_id(f"variety/{name}"),
                    name=name,
                )
                for name in VARIETY_NAMES
            }

            db.add_all(varieties.values())

            # --------------------------------
            # Farms と SVG
            # --------------------------------

            farms = []

            for farm_index in range(2):

                farm_id = make_id(f"farm/{farm_index}")

                elements = []

                # 1ファームにつき最大8区画
                for area_index in range(8):

                    cultivation_index = farm_index * 8 + area_index

                    if cultivation_index >= 15:
                        break

                    area_id = make_id(f"area/{cultivation_index}")

                    x = 20 + (area_index % 4) * 185
                    y = 20 + (area_index // 4) * 165

                    elements.append(
                        {
                            "tag": "rect",
                            "attributes": {
                                "x": str(x),
                                "y": str(y),
                                "width": "155",
                                "height": "130",
                                "fill": "#dcebd5",
                                "stroke": "#66865c",
                                "stroke-width": "2",
                                "data-id": str(area_id),
                            },
                        }
                    )

                farm = Farms(
                    id=farm_id,
                    name=f"家庭菜園 {farm_index + 1}",
                    svg_data={
                        "viewBox": "0 0 800 400",
                        "elements": elements,
                    },
                )

                farms.append(farm)

            db.add_all(farms)
            db.flush()

            # --------------------------------
            # Cultivations と Records
            # --------------------------------

            cultivation_index = 0

            for variety_name, settings in CROP_SETTINGS.items():

                for cycle_index, sow_date_text in enumerate(settings["sow_dates"]):

                    sow_date = date.fromisoformat(sow_date_text)

                    cultivation_id = make_id(
                        f"cultivation/{variety_name}/{cycle_index}"
                    )

                    area_id = make_id(f"area/{cultivation_index}")

                    farm = farms[0] if cultivation_index < 8 else farms[1]

                    # 作付け面積を変える
                    area_size = [2.0, 3.0, 4.0][cycle_index]

                    cultivation = Cultivations(
                        id=cultivation_id,
                        name=(
                            f"{settings['crop']}"
                            f"26{cycle_index + 1:02d}"
                            f"{cultivation_index + 1:02d}"
                        ),
                        variety_id=varieties[variety_name].id,
                        farm_id=farm.id,
                        area_id=area_id,
                        area_size=area_size,
                    )

                    db.add(cultivation)

                    # 収穫量に差をつける
                    yield_factors = [0.75, 1.0, 1.25]
                    factor = yield_factors[cycle_index]

                    total_weight = settings["base_yield"] * factor

                    total_count = round(settings["base_count"] * factor)

                    harvest_date = sow_date + timedelta(days=settings["harvest_days"])

                    # ----------------------------
                    # 作業記録
                    # ----------------------------

                    records = []

                    def add_record(
                        record_date,
                        work_name,
                        amount=None,
                        unit=None,
                        memo="",
                    ):
                        records.append(
                            Records(
                                date=record_date,
                                cultivation_id=cultivation_id,
                                work_type_id=work_types[work_name].id,
                                amount=amount,
                                unit=unit,
                                memo=memo,
                            )
                        )

                    # 播種
                    add_record(
                        sow_date,
                        "播種",
                        100,
                        "粒",
                        "播種を実施",
                    )

                    # 間引き
                    add_record(
                        sow_date + timedelta(days=15),
                        "間引き",
                        round(total_count * 1.2),
                        "株",
                        "間引き後の栽培株数",
                    )

                    # 追肥 2回
                    for days in [30, 50]:
                        add_record(
                            sow_date + timedelta(days=days),
                            "追肥",
                            1.0,
                            "kg",
                            "追肥を実施",
                        )

                    # 水やり 4回
                    for days in [3, 10, 20, 40]:
                        add_record(
                            sow_date + timedelta(days=days),
                            "水やり",
                            5.0,
                            "L",
                            "水やりを実施",
                        )

                    # 収穫重量を3回に分割
                    weight_ratios = [0.4, 0.35, 0.25]

                    # 収穫数量も3回に分割
                    count_ratios = [0.4, 0.35, 0.25]

                    for harvest_index in range(3):

                        harvest_day = harvest_date + timedelta(days=harvest_index * 7)

                        weight = round(
                            total_weight * weight_ratios[harvest_index],
                            2,
                        )

                        count = round(total_count * count_ratios[harvest_index])

                        # 収穫（重量）
                        add_record(
                            harvest_day,
                            "収穫（重量）",
                            weight,
                            "kg",
                            "収穫重量を計測",
                        )

                        # 収穫（数量）
                        add_record(
                            harvest_day,
                            "収穫（数量）",
                            count,
                            settings["quantity_unit"],
                            "収穫数量を記録",
                        )

                    db.add_all(records)

                    cultivation_index += 1

            # --------------------------------
            # 保存
            # --------------------------------

            db.commit()

            print("ダミーデータの登録が完了しました。")
            print(f"ファーム数: {len(farms)}")
            print(f"品種数: {len(varieties)}")
            print(f"栽培単位数: {cultivation_index}")
            print(
                f"作業記録数: " f"{sum(1 for _ in db.scalars(select(Records)).all())}"
            )

        except Exception:
            db.rollback()
            raise


if __name__ == "__main__":
    seed()
