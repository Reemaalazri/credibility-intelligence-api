// This file loads and displays claims from the API, with support for search, filtering, ordering, and speaker-based lookup.
document.addEventListener("DOMContentLoaded", () => {
    updateNavbar();
    bindLogoutButtons();
  
    const form = document.getElementById("claimsForm");
    const bySpeakerBtn = document.getElementById("bySpeakerBtn");
  
    loadClaims();
  
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      await loadClaims();
    });
  
    bySpeakerBtn.addEventListener("click", async () => {
      await loadClaimsBySpeaker();
    });
  });
  
  async function loadClaims() {
    const search = document.getElementById("search").value.trim();
    const label = document.getElementById("label").value;
    const ordering = document.getElementById("ordering").value;
  
    let query = "/api/claims/?";
    const params = new URLSearchParams();
  
    if (search) params.append("search", search);
    if (label) params.append("label", label);
    if (ordering) params.append("ordering", ordering);
  
    query += params.toString();
  
    const response = await apiGet(query);
  
    if (!response.ok) {
      showClaimsError("Could not load claims.");
      return;
    }
  
    const data = await response.json();
    renderClaims(data.results || []);
  }
  
  async function loadClaimsBySpeaker() {
    const speaker = document.getElementById("speaker").value.trim();
  
    if (!speaker) {
      showClaimsError("Please enter a speaker name.");
      return;
    }
  
    const response = await apiGet(`/api/claims/by-speaker/${encodeURIComponent(speaker)}/`);
  
    if (!response.ok) {
      showClaimsError("Could not load claims for that speaker.");
      return;
    }
  
    const data = await response.json();
    renderClaims(data.results || []);
  }
  
  function renderClaims(claims) {
    const container = document.getElementById("claimsResults");
    container.innerHTML = "";
  
    if (!claims.length) {
      container.innerHTML = `<div class="alert alert-warning">No claims found.</div>`;
      return;
    }
  
    claims.forEach(claim => {
      const card = document.createElement("div");
      card.className = "card claim-card shadow-sm";
      card.innerHTML = `
        <div class="card-body">
          <h5 class="card-title">${claim.statement || "No statement"}</h5>
          <p class="mb-1"><strong>Speaker:</strong> ${claim.speaker || "Unknown"}</p>
          <p class="mb-1"><strong>Label:</strong> ${claim.label || "N/A"}</p>
          <p class="mb-1"><strong>Subjects:</strong> ${claim.subjects || "N/A"}</p>
          <p class="mb-2"><strong>Context:</strong> ${claim.context || "N/A"}</p>
          <a href="${claim.url}" target="_blank" class="btn btn-outline-primary btn-sm">Open API Record</a>
        </div>
      `;
      container.appendChild(card);
    });
  }
  
  function showClaimsError(message) {
    document.getElementById("claimsResults").innerHTML =
      `<div class="alert alert-danger">${message}</div>`;
  }