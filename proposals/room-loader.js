(async () => {
  const lockedProduct = document.body.dataset.proposalProduct;
  const fallback = document.getElementById("roomFallback");

  try {
    const response = await fetch("../index.html", { cache: "no-cache" });
    if (!response.ok) throw new Error(`Proposal template returned ${response.status}`);

    const template = new DOMParser().parseFromString(await response.text(), "text/html");
    template.body.querySelectorAll("script").forEach(script => script.remove());
    document.body.innerHTML = template.body.innerHTML;
    document.body.dataset.proposalProduct = lockedProduct;

    const app = document.createElement("script");
    app.src = "../app.js?v=20260922d";
    app.defer = true;
    app.addEventListener("error", () => {
      document.body.innerHTML = '<main class="room-error"><h1>Proposal room unavailable</h1><p>Please email <a href="mailto:darnleyweekes@prime24ai.com">darnleyweekes@prime24ai.com</a>.</p></main>';
    });
    document.body.appendChild(app);
  } catch (error) {
    if (fallback) {
      fallback.hidden = false;
      fallback.querySelector("p").textContent = "The proposal room could not load. Please use the email link below.";
    }
    console.error(error);
  }
})();
