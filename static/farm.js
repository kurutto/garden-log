(function () {
  const generateBtn = document.getElementById("generateBtn");
  const farmContainer = document.getElementById("farmContainer");
  const createSVGElement = (tag) => {
    return document.createElementNS("http://www.w3.org/2000/svg", tag);
  };

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
  generateBtn.addEventListener("click", () => {
    farmContainer.innerHTML = "";
    // フォームに入力された値を元にsvg要素を生成する
    width = Number(document.getElementById("farmWidth").value) * 0.8;
    height = Number(document.getElementById("farmHeight").value) * 0.8;
    farm.setAttribute("viewBox", `0 0 ${width} ${height}`);

    //　四角形とドラックポイントの箱を用意する
    rects[0] = {};
    rects[0].rect = createSVGElement("rect");
    rects[0].rect.setAttribute("data-id", "0");
    farm.appendChild(rects[0].rect);

    rects[0].left = 10;
    rects[0].top = 10;
    rects[0].right = width - 10;
    rects[0].bottom = height - 10;

    rects[0].drugPointLT = createDrugPoint();
    rects[0].drugPointRT = createDrugPoint();
    rects[0].drugPointLB = createDrugPoint();
    rects[0].drugPointRB = createDrugPoint();
    rects[0].drugPointLT.setAttribute("data-id", "0");
    rects[0].drugPointRT.setAttribute("data-id", "0");
    rects[0].drugPointLB.setAttribute("data-id", "0");
    rects[0].drugPointRB.setAttribute("data-id", "0");

    farmContainer.appendChild(farm);

    // 初期表示
    updateVertices(rects[0]);
    setupDrag(rects[0].drugPointLT, (event) =>
      drugPointMove(rects[0], event, "LT"),
    );
    setupDrag(rects[0].drugPointRT, (event) =>
      drugPointMove(rects[0], event, "RT"),
    );
    setupDrag(rects[0].drugPointLB, (event) =>
      drugPointMove(rects[0], event, "LB"),
    );
    setupDrag(rects[0].drugPointRB, (event) =>
      drugPointMove(rects[0], event, "RB"),
    );

    setupDrag(rects[0].rect, (event) => {
      const point = getSVGPoint(event, farm);
      if (!rects[0].previousPoint) {
        rects[0].previousPoint = point;
        return;
      }
      let dx = point.x - rects[0].previousPoint.x;
      let dy = point.y - rects[0].previousPoint.y;

      dx = clamp(dx, -rects[0].left, width - rects[0].right);
      dy = clamp(dy, -rects[0].top, height - rects[0].bottom);

      rects[0].left += dx;
      rects[0].right += dx;
      rects[0].top += dy;
      rects[0].bottom += dy;

      rects[0].previousPoint = point;
      updateVertices(rects[0]);
    });
  });

  let createRectDragging = false;
  let isRectCreated = false;
  let lt = [10, 10];
  let index;
  farm.addEventListener("pointerdown", (e) => {
    if (e.target !== farm) return;
    createRectDragging = true;
    const point = getSVGPoint(e, farm);
    lt = [point.x, point.y];
    index = rects.length;
    rects[index] = {};
  });
  farm.addEventListener("pointermove", (e) => {
    if (!createRectDragging) return;
    const rectObj = rects[index];
    const point = getSVGPoint(e, farm);
    if (!isRectCreated) {
      rectObj.rect = createSVGElement("rect");
      rectObj.rect.setAttribute("data-id", index);
      rectObj.drugPointLT = createDrugPoint();
      rectObj.drugPointRT = createDrugPoint();
      rectObj.drugPointLB = createDrugPoint();
      rectObj.drugPointRB = createDrugPoint();
      rectObj.left = lt[0];
      rectObj.right = clamp(point.x, lt[0], width);
      rectObj.top = lt[1];
      rectObj.bottom = clamp(point.y, lt[1], height);
      updateVertices(rectObj);

      farm.appendChild(rectObj.rect);
      isRectCreated = true;
      setupDrag(rectObj.drugPointLT, (e) => drugPointMove(rectObj, e, "LT"));
      setupDrag(rectObj.drugPointRT, (e) => drugPointMove(rectObj, e, "RT"));
      setupDrag(rectObj.drugPointLB, (e) => drugPointMove(rectObj, e, "LB"));
      setupDrag(rectObj.drugPointRB, (e) => drugPointMove(rectObj, e, "RB"));

      setupDrag(rectObj.rect, (e) => {
        const point = getSVGPoint(e, farm);
        if (!rectObj.previousPoint) {
          rectObj.previousPoint = point;
          return;
        }
        let dx = point.x - rectObj.previousPoint.x;
        let dy = point.y - rectObj.previousPoint.y;

        dx = clamp(dx, -rectObj.left, width - rectObj.right);
        dy = clamp(dy, -rectObj.top, height - rectObj.bottom);

        rectObj.left += dx;
        rectObj.right += dx;
        rectObj.top += dy;
        rectObj.bottom += dy;

        rectObj.previousPoint = point;
        updateVertices(rectObj);
      });
    }

    rectObj.right = clamp(point.x, lt[0], width);
    rectObj.bottom = clamp(point.y, lt[1], height);
    updateVertices(rectObj);
  });
  farm.addEventListener("pointerup", (e) => {
    if (!createRectDragging) return;
    createRectDragging = false;
    isRectCreated = false;
    lt = [0, 0];
    if (rects[index]?.rect === undefined) {
      rects.pop();
    }
    index = undefined;
  });
})();
