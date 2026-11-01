(function () {
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
