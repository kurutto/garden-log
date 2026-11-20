import {
  farmsData,
  getFarmData,
  CreateFarm,
  createSVGElement,
  updateVertices,
  onObjDrug,
  createElem,
  CreateDeleteElemWithinSVG,
  createSvgData,
} from "./farm.js";
import { modal } from "./modal.js";
const closeTxt = "*";
(function () {
  // 作業記録エリアのフォームをコントロール
  const vegetableSelect = document.getElementById("vegetable_id");
  const workSelect = document.getElementById("work");
  const amountInput = document.getElementById("harvest_amount");
  const quantityHelp = document.getElementById("quantity-help");
  const recordArea = document.getElementById("record_area");

  vegetableSelect.addEventListener("change", () => {
    recordArea.textContent = "";
    const option = vegetableSelect.selectedOptions[0];
    const farmId = option?.dataset.farm;
    const areaId = option?.dataset.area;
    const farmData = getFarmData(farmsData, farmId);
    CreateFarm(recordArea, farmData);
    const rects = recordArea.getElementsByTagName("rect");
    Array.from(rects).forEach((elem) => {
      if (elem.dataset.id === areaId) {
        elem.classList.add("is-current");
      }
    });
  });

  function updateQuantityField() {
    const isHarvest = workSelect.value === "収穫";
    amountInput.required = isHarvest;
    quantityHelp.hidden = !isHarvest;
  }

  workSelect.addEventListener("change", updateQuantityField);
  updateQuantityField();

  // 記録一覧エリアの編集、削除
  const recordCards = document.querySelectorAll(".record-card");

  recordCards.forEach((card) => {
    const editButton = card.querySelector(".edit-btn");
    const submitButton = card.querySelector(".submit-btn");
    const cancelButton = card.querySelector(".cancel-btn");
    const recordDataElements = card.querySelectorAll(".record-data");
    const editDataElements = card.querySelectorAll(".edit-data");
    let isEditing = false;
    const changeState = () => {
      if (isEditing) {
        recordDataElements.forEach((elem) => (elem.hidden = true));
        editDataElements.forEach((elem) => (elem.hidden = false));
        editButton.hidden = true;
        submitButton.hidden = false;
        cancelButton.hidden = false;
      } else {
        recordDataElements.forEach((elem) => (elem.hidden = false));
        editDataElements.forEach((elem) => (elem.hidden = true));
        editButton.hidden = false;
        submitButton.hidden = true;
        cancelButton.hidden = true;
      }
    };
    changeState();
    editButton.addEventListener("click", () => {
      isEditing = !isEditing;
      changeState();
    });
    cancelButton.addEventListener("click", () => {
      isEditing = !isEditing;
      changeState();
    });
    submitButton.addEventListener("click", () => {
      isEditing = !isEditing;
      changeState();
    });
  });
})();

// 畑新規登録
(function () {
  const modalLinkItem = document.querySelector(".js-modal-link-item");
  const { modalClose } = modal(modalLinkItem, undefined, closeTxt);
  const generateBtn = document.getElementById("generateBtn");
  const farmContainer = document.getElementById("farmContainer");

  const farm = createSVGElement("svg");
  let width = 0;
  let height = 0;
  let rects = []; // 生成された四角形の情報を格納する配列

  //svgを新規追加
  generateBtn.addEventListener("click", () => {
    farmContainer.innerHTML = "";
    // フォームに入力された値を元にsvg要素を生成する
    width = Number(document.getElementById("farmWidth").value) * 0.8;
    height = Number(document.getElementById("farmHeight").value) * 0.8;
    farm.setAttribute("viewBox", `0 0 ${width} ${height}`);

    //　四角形とドラックポイントの箱を用意する
    const uuid = crypto.randomUUID();
    createElem(0, 10, 10, width - 10, height - 10, farm, rects, uuid);

    farmContainer.appendChild(farm);

    // 初期表示
    updateVertices(rects[0]);

    onObjDrug(rects[0], farm, width, height);
    CreateDeleteElemWithinSVG(farm, width, height, rects);
  });

  //データベースにsvgデータを保存
  const addFarm = () => {
    const farmName = document.querySelector("#farmName");
    const farmNameValue = farmName.value;
    const data = createSvgData(farmNameValue, farm);
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

// 野菜新規登録時のエリア指定・変更
(function () {
  const farms = document.getElementById("farms");
  const selectedFarmContainer = document.getElementById(
    "selectedFarmContainer",
  );
  const selectedAreaText = document.getElementById("selected_area_text");

  let farmData;
  const selectFarm = () => {
    selectedFarmContainer.innerHTML = "";
    const farmId = farms.value;
    farmData = getFarmData(farmsData, farmId);
    const { farmSVG, width, height, rects } = CreateFarm(
      selectedFarmContainer,
      farmData,
      onObjDrug,
    );
    CreateDeleteElemWithinSVG(farmSVG, width, height, rects);
  };
  const inputAreaId = document.getElementById("area_id");
  const inputFarmSvg = document.getElementById("farm_svg");

  selectedFarmContainer.addEventListener("click", (e) => {
    selectedFarmContainer
      .querySelector(".is-current")
      ?.classList.remove("is-current");
    if (e.target.tagName == "rect") e.target.classList.add("is-current");
    const areaId = e.target.dataset.id;
    const svg = selectedFarmContainer.querySelector("svg");
    if (!areaId) return;
    inputAreaId.value = areaId;
    inputFarmSvg.value = JSON.stringify(createSvgData(farmData.farm_name, svg));
    selectedAreaText.textContent = `ファーム名：${farmData.farm_name}、エリアID：${areaId}`;
  });
  farms.addEventListener("change", selectFarm);
})();
