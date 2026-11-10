(function () {
  const generateBtn = document.getElementById("generateBtn");
  const farmContainer = document.getElementById("farmContainer");
  const createSVGElement = (tag) => {
    return document.createElementNS("http://www.w3.org/2000/svg", tag);
  };
  // 数値を指定範囲内に制限する
  const clamp = (value, min, max) => {
    return Math.max(min, Math.min(max, value));
  };
  const MinSize = 20; // 四角形の最小サイズ
  generateBtn.addEventListener("click", () => {
    farmContainer.innerHTML = "";
    // フォームに入力された値を元にsvg要素を生成する
    const width = Number(document.getElementById("farmWidth").value) * 0.8;
    const height = Number(document.getElementById("farmHeight").value) * 0.8;
    const farm = createSVGElement("svg");
    farm.setAttribute("viewBox", `0 0 ${width} ${height}`);

    //　四角形の位置情報の初期値を設定
    let left = 10;
    let top = 10;
    let right = width - 10;
    let bottom = height - 10;

    //　四角形とドラックポイントの箱を用意する
    const rect = createSVGElement("rect");
    farm.appendChild(rect);

    const createDrugPoint = () => {
      const circle = createSVGElement("circle");
      circle.setAttribute("r", "10");
      circle.setAttribute("fill", "red");
      farm.appendChild(circle);
      return circle;
    };
    const drugPointLT = createDrugPoint();
    const drugPointRT = createDrugPoint();
    const drugPointLB = createDrugPoint();
    const drugPointRB = createDrugPoint();

    farmContainer.appendChild(farm);

    //　各頂点の座標でrectとドラッグポイントの属性を更新する関数
    const updateVertices = () => {
      rect.setAttribute("x", left);
      rect.setAttribute("y", top);
      rect.setAttribute("width", right - left);
      rect.setAttribute("height", bottom - top);
      drugPointLT.setAttribute("cx", left);
      drugPointLT.setAttribute("cy", top);
      drugPointRT.setAttribute("cx", right);
      drugPointRT.setAttribute("cy", top);
      drugPointLB.setAttribute("cx", left);
      drugPointLB.setAttribute("cy", bottom);
      drugPointRB.setAttribute("cx", right);
      drugPointRB.setAttribute("cy", bottom);
    };

    // 初期表示
    updateVertices();

    // viewPortの座標系をsvgの座標系に変換する関数
    const getSVGPoint = (event, svg) => {
      const point = svg.createSVGPoint();

      point.x = event.clientX;
      point.y = event.clientY;

      return point.matrixTransform(svg.getScreenCTM().inverse());
    };

    // 各頂点の位置を更新する関数
    const drugPointMove = (event, corner) => {
      const point = getSVGPoint(event, farm);

      switch (corner) {
        case "LT":
          left = clamp(point.x, 0, right - MinSize);
          top = clamp(point.y, 0, bottom - MinSize);
          break;
        case "RT":
          top = clamp(point.y, 0, bottom - MinSize);
          right = clamp(point.x, left + MinSize, width);
          break;
        case "LB":
          left = clamp(point.x, 0, right - MinSize);
          bottom = clamp(point.y, top + MinSize, height);
          break;
        case "RB":
          right = clamp(point.x, left + MinSize, width);
          bottom = clamp(point.y, top + MinSize, height);
          break;
      }

      updateVertices();
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
    setupDrag(drugPointLT, (event) => drugPointMove(event, "LT"));
    setupDrag(drugPointRT, (event) => drugPointMove(event, "RT"));
    setupDrag(drugPointLB, (event) => drugPointMove(event, "LB"));
    setupDrag(drugPointRB, (event) => drugPointMove(event, "RB"));

    setupDrag(rect, (event) => {
      const point = getSVGPoint(event, farm);
      if (!rect.previousPoint) {
        rect.previousPoint = point;
        return;
      }
      let dx = point.x - rect.previousPoint.x;
      let dy = point.y - rect.previousPoint.y;

      dx = clamp(dx, -left, width - right);
      dy = clamp(dy, -top, height - bottom);

      left += dx;
      right += dx;
      top += dy;
      bottom += dy;

      rect.previousPoint = point;
      updateVertices();
    });
  });
})();
