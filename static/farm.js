import { modal } from "./modal.js";
const closeTxt = "*";
const createSVGElement = (tag) => {
  return document.createElementNS("http://www.w3.org/2000/svg", tag);
};
(function () {
  const modalLinkItem = document.querySelector(".js-modal-link-item");
  const { modalClose } = modal(modalLinkItem, undefined, closeTxt);
  // const modalClose = modal(modalItem, "");
  const generateBtn = document.getElementById("generateBtn");
  const farmContainer = document.getElementById("farmContainer");

  const farm = createSVGElement("svg");
  let width = 0;
  let height = 0;
  // 数値を指定範囲内に制限する
  const clamp = (value, min, max) => {
    return Math.max(min, Math.min(max, value));
  };
  const MinSize = 20; // 四角形の最小サイズ
  let rects = []; // 生成された四角形の情報を格納する配列

  //　各頂点の座標でrectとドラッグポイントの属性を更新する関数
  const updateVertices = (rectObj) => {
    rectObj.rect.setAttribute("x", rectObj.left);
    rectObj.rect.setAttribute("y", rectObj.top);
    rectObj.rect.setAttribute("width", rectObj.right - rectObj.left);
    rectObj.rect.setAttribute("height", rectObj.bottom - rectObj.top);
    rectObj.drugPointLT.setAttribute("cx", rectObj.left);
    rectObj.drugPointLT.setAttribute("cy", rectObj.top);
    rectObj.drugPointRT.setAttribute("cx", rectObj.right);
    rectObj.drugPointRT.setAttribute("cy", rectObj.top);
    rectObj.drugPointLB.setAttribute("cx", rectObj.left);
    rectObj.drugPointLB.setAttribute("cy", rectObj.bottom);
    rectObj.drugPointRB.setAttribute("cx", rectObj.right);
    rectObj.drugPointRB.setAttribute("cy", rectObj.bottom);
  };
  const createDrugPoint = () => {
    const circle = createSVGElement("circle");
    circle.setAttribute("r", "10");
    circle.setAttribute("fill", "red");
    farm.appendChild(circle);
    return circle;
  };

  // viewPortの座標系をsvgの座標系に変換する関数
  const getSVGPoint = (event, svg) => {
    const point = svg.createSVGPoint();

    point.x = event.clientX;
    point.y = event.clientY;

    return point.matrixTransform(svg.getScreenCTM().inverse());
  };
  // 各頂点の位置を更新する関数
  const drugPointMove = (rectObj, event, corner) => {
    const point = getSVGPoint(event, farm);

    switch (corner) {
      case "LT":
        rectObj.left = clamp(point.x, 0, rectObj.right - MinSize);
        rectObj.top = clamp(point.y, 0, rectObj.bottom - MinSize);
        break;
      case "RT":
        rectObj.top = clamp(point.y, 0, rectObj.bottom - MinSize);
        rectObj.right = clamp(point.x, rectObj.left + MinSize, width);
        break;
      case "LB":
        rectObj.left = clamp(point.x, 0, rectObj.right - MinSize);
        rectObj.bottom = clamp(point.y, rectObj.top + MinSize, height);
        break;
      case "RB":
        rectObj.right = clamp(point.x, rectObj.left + MinSize, width);
        rectObj.bottom = clamp(point.y, rectObj.top + MinSize, height);
        break;
    }

    updateVertices(rectObj);
  };

  const setupDrag = (drugPoint, onMove) => {
    let isDragging = false;

    drugPoint.addEventListener("pointerdown", (event) => {
      isDragging = true;
      drugPoint.setPointerCapture(event.pointerId);
    });
    drugPoint.addEventListener("pointermove", (event) => {
      if (!isDragging) return;
      onMove(event);
    });
    drugPoint.addEventListener("pointerup", (event) => {
      if (!isDragging) return;
      isDragging = false;
    });
  };
  const onObjDrug = (obj) => {
    setupDrag(obj.drugPointLT, (event) => drugPointMove(obj, event, "LT"));
    setupDrag(obj.drugPointRT, (event) => drugPointMove(obj, event, "RT"));
    setupDrag(obj.drugPointLB, (event) => drugPointMove(obj, event, "LB"));
    setupDrag(obj.drugPointRB, (event) => drugPointMove(obj, event, "RB"));

    setupDrag(obj.rect, (event) => {
      const point = getSVGPoint(event, farm);
      if (!obj.previousPoint) {
        obj.previousPoint = point;
        return;
      }
      let dx = point.x - obj.previousPoint.x;
      let dy = point.y - obj.previousPoint.y;

      dx = clamp(dx, -obj.left, width - obj.right);
      dy = clamp(dy, -obj.top, height - obj.bottom);

      obj.left += dx;
      obj.right += dx;
      obj.top += dy;
      obj.bottom += dy;

      obj.previousPoint = point;
      updateVertices(obj);
      obj.rect.addEventListener("pointerup", () => {
        obj.previousPoint = undefined;
      });
    });
  };
  const createElem = (index, left, top, right, bottom) => {
    const uuid = crypto.randomUUID();
    rects[index] = {};
    rects[index].rect = createSVGElement("rect");
    rects[index].rect.setAttribute("data-id", uuid);
    farm.appendChild(rects[0].rect);

    rects[index].left = left;
    rects[index].top = top;
    rects[index].right = right;
    rects[index].bottom = bottom;

    rects[index].drugPointLT = createDrugPoint();
    rects[index].drugPointRT = createDrugPoint();
    rects[index].drugPointLB = createDrugPoint();
    rects[index].drugPointRB = createDrugPoint();
    rects[index].drugPointLT.setAttribute("data-id", uuid);
    rects[index].drugPointRT.setAttribute("data-id", uuid);
    rects[index].drugPointLB.setAttribute("data-id", uuid);
    rects[index].drugPointRB.setAttribute("data-id", uuid);
  };
  generateBtn.addEventListener("click", () => {
    farmContainer.innerHTML = "";
    // フォームに入力された値を元にsvg要素を生成する
    width = Number(document.getElementById("farmWidth").value) * 0.8;
    height = Number(document.getElementById("farmHeight").value) * 0.8;
    farm.setAttribute("viewBox", `0 0 ${width} ${height}`);

    //　四角形とドラックポイントの箱を用意する
    createElem(0, 10, 10, width - 10, height - 10);

    farmContainer.appendChild(farm);

    // 初期表示
    updateVertices(rects[0]);

    onObjDrug(rects[0]);
  });

  let createRectDragging = false;
  let isRectCreated = false;
  let lt = [10, 10];
  let index;
  let pressTimer;
  farm.addEventListener("pointerdown", (e) => {
    if (e.target !== farm) {
      pressTimer = setTimeout(() => {
        const deleteArea = confirm("削除しますか");
        if (deleteArea) {
          const deleteId = e.target.dataset.id;
          const deleteIndex = rects.findIndex((rect) => rect.id === deleteId);
          rects.splice(deleteIndex, 1);
          const deleteItems = farm.querySelectorAll(`[data-id="${deleteId}"]`);
          deleteItems.forEach((item) => item.remove());
        } else {
          return;
        }
      }, 1000);
    } else {
      createRectDragging = true;
      const point = getSVGPoint(e, farm);
      lt = [point.x, point.y];
      index = rects.length;
    }
  });

  farm.addEventListener("pointerleave", () => {
    clearTimeout(pressTimer);
  });

  farm.addEventListener("pointercancel", () => {
    clearTimeout(pressTimer);
  });
  farm.addEventListener("pointermove", (e) => {
    clearTimeout(pressTimer);
    if (!createRectDragging) return;
    const point = getSVGPoint(e, farm);
    if (!isRectCreated) {
      createElem(
        index,
        lt[0],
        lt[1],
        clamp(point.x, lt[0], width),
        clamp(point.y, lt[1], height),
      );
      const rectObj = rects[index];
      updateVertices(rectObj);

      farm.appendChild(rectObj.rect);
      isRectCreated = true;
      onObjDrug(rectObj);
    }

    rects[index].right = clamp(point.x, lt[0], width);
    rects[index].bottom = clamp(point.y, lt[1], height);
    updateVertices(rects[index]);
  });
  farm.addEventListener("pointerup", (e) => {
    clearTimeout(pressTimer);
    if (!createRectDragging) return;
    createRectDragging = false;
    isRectCreated = false;
    lt = [0, 0];
    if (rects[index]?.rect === undefined) {
      rects.pop();
    }
    index = undefined;
  });

  const addFarm = () => {
    const farmName = document.querySelector("#farmName");
    const farmNameValue = farmName.value;
    // const svg = farm.querySelector("svg");
    const svgData = {
      viewBox: farm.getAttribute("viewBox"),
      elements: [...farm.querySelectorAll("rect, circle")].map((elem) => {
        const attributes = {};
        [...elem.attributes].forEach((attr) => {
          attributes[attr.name] = attr.value;
        });
        return { tag: elem.tagName, attributes };
      }),
    };
    const data = {
      farmName: farmNameValue,
      svgData,
    };
    fetch("/farm", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    modalClose();
  };

  const addFarmBtn = document.getElementById("addFarmBtn");
  addFarmBtn.addEventListener("click", addFarm);
})();

(function () {
  const modalItem = document.getElementById("js-select-farm-modal-box");
  const { modalOpen, modalClose } = modal(undefined, modalItem, closeTxt);
  const farms = document.getElementById("farms");
  const selectedFarmContainer = document.getElementById(
    "selectedFarmContainer",
  );
  const selectedArea = document.getElementById("selected_area");
  const selectedAreaText = document.getElementById("selected_area_text");
  const farmElement = document.getElementById("farm-data");
  const farmsData = JSON.parse(farmElement.textContent);
  let farmId;
  let farmData;
  const selectFarm = () => {
    modalOpen();
    selectedFarmContainer.innerHTML = "";
    farmId = farms.value;
    farmData = farmsData.find((item) => item.id === farmId);
    console.log("farmId", farmId);

    const selectedFarm = createSVGElement("svg");
    selectedFarm.setAttribute("viewBox", farmData.svg_data.viewBox);
    farmData.svg_data.elements.forEach((elem) => {
      const tag = createSVGElement(elem.tag);
      Object.entries(elem.attributes).forEach(([key, value]) => {
        tag.setAttribute(key, value);
      });
      selectedFarm.appendChild(tag);
    });
    selectedFarmContainer.appendChild(selectedFarm);
    console.log(document.body.className);
  };
  const inputAreaId = document.getElementById("area_id");
  selectedFarmContainer.addEventListener("click", (e) => {
    const areaId = e.target.dataset.id;
    if (!areaId) return;
    inputAreaId.value = areaId;
    selectedAreaText.textContent = `ファーム名：${farmData.farm_name}、エリアID：${areaId}`;
    modalClose();
  });
  farms.addEventListener("change", selectFarm);
})();
