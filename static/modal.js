export const modal = (modalLinkItem, modalItem, closeTxt) => {
  const body = document.body;
  const overlay = document.querySelector(".js-overlay");
  const target = modalItem
    ? modalItem
    : document.getElementById(modalLinkItem.dataset.modalId);

  let close;
  let scrollPos;

  const modalOpen = () => {
    console.log("modalOpen実行");
    scrollPos = window.pageYOffset || document.documentElement.scrollTop;
    body.classList.add("js-modal-open");
    body.style.top = `-${scrollPos}px`;
    close = document.createElement("div");
    close.setAttribute("class", "modal-close js-modal-close");
    close.textContent = closeTxt;
    target.append(close);
    const closeBtns = target.querySelectorAll(".js-modal-close");
    target.classList.add("js-open");
    overlay.classList.add("js-open");
    overlay.addEventListener(
      "click",
      () => {
        modalClose();
      },
      { once: true },
    );
    closeBtns.forEach((closeBtn) => {
      closeBtn.addEventListener(
        "click",
        () => {
          modalClose();
        },
        { once: true },
      );
    });
  };

  if (modalLinkItem) {
    modalLinkItem.addEventListener("click", (e) => {
      e.preventDefault();
      modalOpen();
    });
  }
  const modalClose = () => {
    console.log("modalClose実行");
    console.log(body.classList.contains("js-modal-open"));
    body.classList.remove("js-modal-open");
    console.log(body.classList.contains("js-modal-open"));
    body.style.top = "0px";
    window.scrollTo({
      top: scrollPos,
      left: 0,
      behavior: "instant",
    });
    target.classList.add("fade-out");
    overlay.classList.add("fade-out");
    setTimeout(() => {
      close.remove();
      target.classList.remove("js-open", "fade-out");
      overlay.classList.remove("js-open", "fade-out");
    }, 500);
  };
  return { modalOpen, modalClose };
};
