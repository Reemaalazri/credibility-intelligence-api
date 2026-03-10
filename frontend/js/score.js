document.addEventListener("DOMContentLoaded", () => {
    updateNavbar();
    bindLogoutButtons();
  
    const form = document.getElementById("scoreForm");
    form.addEventListener("submit", handleScore);
  });
  
  async function handleScore(e) {
    e.preventDefault();
  
    const text = document.getElementById("claimText").value.trim();
    const resultBox = document.getElementById("scoreResult");
  
    if (!text) {
      resultBox.innerHTML = `<div class="alert alert-warning">Please enter a claim.</div>`;
      return;
    }
  
    if (!getAccessToken()) {
      resultBox.innerHTML = `<div class="alert alert-danger">Please log in first to use the score endpoint.</div>`;
      return;
    }
  
    resultBox.innerHTML = `<div class="alert alert-info">Checking claim...</div>`;
  
    try {
      const response = await apiPost("/api/score/", { text }, true);
      const data = await response.json();
  
      if (!response.ok) {
        resultBox.innerHTML = `
          <div class="alert alert-danger">
            ${data.error || data.detail || "Failed to score claim."}
          </div>
        `;
        return;
      }
  
      const summary = data.summary || {};
      const verdict = summary.final_verdict || "unknown";
      const cred = summary.final_credibility_score ?? 0;
      const risk = summary.final_risk_score ?? 0;
      const confidence = summary.final_confidence ?? 0;
  
      resultBox.innerHTML = `
        <div class="card shadow-sm">
          <div class="card-body">
            <h4 class="mb-3">Credibility Analysis Result</h4>
  
            <p><strong>Claim:</strong> ${data.claim}</p>
            <p><strong>Verdict:</strong> <span class="badge bg-primary result-badge">${verdict}</span></p>
            <p><strong>Credibility Score:</strong> ${cred}/100</p>
            <div class="score-meter mb-3">
              <div class="score-meter-fill bg-success" style="width:${cred}%"></div>
            </div>
  
            <p><strong>Risk Score:</strong> ${risk}/100</p>
            <div class="score-meter mb-3">
              <div class="score-meter-fill bg-danger" style="width:${risk}%"></div>
            </div>
  
            <p><strong>Confidence:</strong> ${confidence}/100</p>
            <div class="score-meter mb-4">
              <div class="score-meter-fill bg-info" style="width:${confidence}%"></div>
            </div>
  
            <div class="section-box">
              <h5>Local Analysis</h5>
              <pre class="json-box">${prettyJSON(data.local_analysis || {})}</pre>
            </div>
  
            <div class="section-box">
              <h5>External Analysis</h5>
              <pre class="json-box">${prettyJSON(data.external_analysis || {})}</pre>
            </div>
  
            <div class="section-box">
              <h5>Fusion</h5>
              <pre class="json-box">${prettyJSON(data.fusion || {})}</pre>
            </div>
          </div>
        </div>
      `;
    } catch (error) {
      resultBox.innerHTML = `<div class="alert alert-danger">Something went wrong while calling the API.</div>`;
    }
  }