console.log("[DealRater] overlay.js loaded");

(function () {
  let box;

  function ensureBox() {
    if (box) return box;

    box = document.createElement("div");
    box.id = "deal-rater-box";
    box.innerText = "Overlay ready";
    document.body.appendChild(box);

    return box;
  }

  window.showLoading = function () {
    console.log("[DealRater] showLoading called");
    const b = ensureBox();
    b.innerText = "Analyzing deal… ⏳";
  };

  // displays returned result for model
  window.showResult = function (result) {
    const b = ensureBox();
    b.innerHTML = `
      <div>${result.score}/100</div>
      <div>$${result.offer}</div>
      <div>$${result.resell}</div>
      <small>${result.reason}</small>
    `;
  };

  window.showError = function () {
    const b = ensureBox();
    b.innerText = "Backend error";
  };
})();
