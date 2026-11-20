//　farm関連の関数 ---------------------------

const farmElement = document.getElementById("farm-data");
export const farmsData = JSON.parse(farmElement.textContent);

// 数値を指定範囲内に制限する
const clamp = (value, min, max) => {
  return Math.max(min, Math.min(max, value));
};

// 四角形の最小サイズ
const MinSize = 20;

// viewPortの座標系をsvgの座標系に変換する関数
const getSVGPoint = (event, svg) => {
  const point = svg.createSVGPoint();

  point.x = event.clientX;
  point.y = event.clientY;

  return point.matrixTransform(svg.getScreenCTM().inverse());
};

// ドラッグポイントを作成
const createDrugPoint = (svg) => {
  const circle = createSVGElement("circle");
  circle.setAttribute("r", "10");
  circle.setAttribute("fill", "red");
  svg.appendChild(circle);
  return circle;
};

// 各頂点の位置を更新する関数
const drugPointMove = (rectObj, event, corner, svg, width, height) => {
  const point = getSVGPoint(event, svg);

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

// ドラッグポイントを動かした時の処理
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

// バックエンドから送られてくるfarmの全データから対象のfarmのデータを取り出す
export const getFarmData = (farmsData, farmId) => {
  return farmsData.find((item) => item.id === farmId);
};

// svgの要素を作成
export const createSVGElement = (tag) => {
  return document.createElementNS("http://www.w3.org/2000/svg", tag);
};

// farmデータからsvgを作成
export const CreateFarm = (container, farmData, onObjDrug) => {
  const farmSVG = createSVGElement("svg");
  const [x, y, width, height] = farmData.svg_data.viewBox
    .split(" ")
    .map(Number);
  let rects = [];
  farmSVG.setAttribute("viewBox", farmData.svg_data.viewBox);
  let index = 0;
  farmData.svg_data.elements.forEach((elem) => {
    if (elem.tag === "rect") {
      const left = Number(elem.attributes.x);
      const top = Number(elem.attributes.y);
      const right = left + Number(elem.attributes.width);
      const bottom = top + Number(elem.attributes.height);
      const uuid = elem.attributes["data-id"];
      createElem(index, left, top, right, bottom, farmSVG, rects, uuid);
      updateVertices(rects[index]);
      onObjDrug ? onObjDrug(rects[index], farmSVG, width, height) : null;
      index++;
    }
    container.appendChild(farmSVG);
  });
  return { farmSVG, width, height, rects };
};

//　各頂点の座標でrectとドラッグポイントの属性を更新する関数
export const updateVertices = (rectObj) => {
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

export const onObjDrug = (obj, svg, width, height) => {
  setupDrag(obj.drugPointLT, (event) =>
    drugPointMove(obj, event, "LT", svg, width, height),
  );
  setupDrag(obj.drugPointRT, (event) =>
    drugPointMove(obj, event, "RT", svg, width, height),
  );
  setupDrag(obj.drugPointLB, (event) =>
    drugPointMove(obj, event, "LB", svg, width, height),
  );
  setupDrag(obj.drugPointRB, (event) =>
    drugPointMove(obj, event, "RB", svg, width, height),
  );

  setupDrag(obj.rect, (event) => {
    const point = getSVGPoint(event, svg);
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

// rect,circle などのsvg要素を作成
export const createElem = (
  index,
  left,
  top,
  right,
  bottom,
  svg,
  rects,
  uuid,
) => {
  rects[index] = {};
  rects[index].rect = createSVGElement("rect");
  rects[index].rect.setAttribute("data-id", uuid);
  svg.appendChild(rects[index].rect);

  rects[index].left = left;
  rects[index].top = top;
  rects[index].right = right;
  rects[index].bottom = bottom;

  rects[index].drugPointLT = createDrugPoint(svg);
  rects[index].drugPointRT = createDrugPoint(svg);
  rects[index].drugPointLB = createDrugPoint(svg);
  rects[index].drugPointRB = createDrugPoint(svg);
  rects[index].drugPointLT.setAttribute("data-id", uuid);
  rects[index].drugPointRT.setAttribute("data-id", uuid);
  rects[index].drugPointLB.setAttribute("data-id", uuid);
  rects[index].drugPointRB.setAttribute("data-id", uuid);
};

//svgの中のrectを追加・削除
export const CreateDeleteElemWithinSVG = (svg, width, height, rects) => {
  let createRectDragging = false;
  let isRectCreated = false;
  let lt = [10, 10];
  let index;
  let pressTimer;
  svg.addEventListener("pointerdown", (e) => {
    if (e.target !== svg) {
      pressTimer = setTimeout(() => {
        const deleteArea = confirm("削除しますか");
        if (deleteArea) {
          const deleteId = e.target.dataset.id;
          const deleteIndex = rects.findIndex((rect) => rect.id === deleteId);
          rects.splice(deleteIndex, 1);
          const deleteItems = svg.querySelectorAll(`[data-id="${deleteId}"]`);
          deleteItems.forEach((item) => item.remove());
        } else {
          return;
        }
      }, 1000);
    } else {
      createRectDragging = true;
      const point = getSVGPoint(e, svg);
      lt = [point.x, point.y];
      index = rects.length;
    }
  });

  svg.addEventListener("pointerleave", () => {
    clearTimeout(pressTimer);
  });

  svg.addEventListener("pointercancel", () => {
    clearTimeout(pressTimer);
  });
  svg.addEventListener("pointermove", (e) => {
    clearTimeout(pressTimer);
    if (!createRectDragging) return;
    const point = getSVGPoint(e, svg);
    if (!isRectCreated) {
      const uuid = crypto.randomUUID();
      createElem(
        index,
        lt[0],
        lt[1],
        clamp(point.x, lt[0], width),
        clamp(point.y, lt[1], height),
        svg,
        rects,
        uuid,
      );
      const rectObj = rects[index];
      updateVertices(rectObj);

      svg.appendChild(rectObj.rect);
      isRectCreated = true;
      onObjDrug(rectObj, svg, width, height);
    }

    rects[index].right = clamp(point.x, lt[0], width);
    rects[index].bottom = clamp(point.y, lt[1], height);
    updateVertices(rects[index]);
  });
  svg.addEventListener("pointerup", (e) => {
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
};

// svgデータをデータベースに送る形に作成
export const createSvgData = (farmName, svg) => {
  const svgData = {
    viewBox: svg.getAttribute("viewBox"),
    elements: [...svg.querySelectorAll("rect")].map((elem) => {
      const attributes = {};
      [...elem.attributes].forEach((attr) => {
        attributes[attr.name] = attr.value;
      });
      return { tag: elem.tagName, attributes };
    }),
  };
  return {
    farmName,
    svgData,
  };
};
