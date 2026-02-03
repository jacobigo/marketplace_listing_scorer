console.log("[DealRater] content.js loaded");

function safe(fn) {
  if (typeof fn !== "function") {
    console.error("[DealRater] overlay function missing");
    return false;
  }
  return true;
}


const seen = new WeakSet();

const observer = new MutationObserver(() => {
  const listings = document.querySelectorAll('[role="link"]');

  listings.forEach(listing => {
    if (seen.has(listing)) return;
    seen.add(listing);

    // calls listener on click of each listing
    listing.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      const data = extractListing(listing);
      if (data) analyzeListing(data);
    });
  });
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

// gets the title, image url, and price
function extractListing(listing) {
    const text = listing.innerText;
    if (!text) return null;

    const lines = text.split("\n").filter(Boolean);
    const priceLine = lines.find(l => l.startsWith("$"));
    if (!priceLine) return null;

    const titleLine = lines.find(l => !l.startsWith("$") && l.toLowerCase() !== "just listed");

    const img = listing.querySelector("img");

    return {
    title: titleLine || lines[0],
    price: parseInt(priceLine.replace(/[^\d]/g, ""), 10),
    image: img ? img.src : null
    };
}

// sends content to python server endpoint
function analyzeListing(data) {
  if (!safe(window.showLoading)) return;

  window.showLoading();

  fetch("http://localhost:8000/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  })
    .then(r => r.json())
    .then(res => window.showResult && window.showResult(res))
    .catch(() => window.showError && window.showError());
}

