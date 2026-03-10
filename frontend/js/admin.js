document.addEventListener("DOMContentLoaded", () => {
    updateNavbar();
    bindLogoutButtons();
  
    if (!getAccessToken()) {
      document.getElementById("adminReportsList").innerHTML =
        `<div class="alert alert-danger">Please log in as admin.</div>`;
      return;
    }
  
    loadAllReports();
  });
  
  async function loadAllReports() {
    const container = document.getElementById("adminReportsList");
    container.innerHTML = `<div class="alert alert-info">Loading all reports...</div>`;
  
    const response = await apiGet("/api/reports/", true);
  
    if (!response.ok) {
      container.innerHTML = `<div class="alert alert-danger">Could not load admin reports. You may not be an admin.</div>`;
      return;
    }
  
    const data = await response.json();
    const reports = data.results || [];
  
    if (!reports.length) {
      container.innerHTML = `<div class="alert alert-warning">No reports available.</div>`;
      return;
    }
  
    container.innerHTML = "";
  
    reports.forEach(report => {
      const card = document.createElement("div");
      card.className = "card report-card shadow-sm";
      card.innerHTML = `
        <div class="card-body">
          <h5 class="card-title">${report.statement_text}</h5>
          <p class="mb-1"><strong>User ID:</strong> ${report.user}</p>
          <p class="mb-1"><strong>Speaker:</strong> ${report.speaker || "Unknown"}</p>
          <p class="mb-1"><strong>Status:</strong> ${report.status}</p>
          <p class="mb-1"><strong>Risk Level:</strong> ${report.risk_level}</p>
          <p class="mb-2"><strong>Reason:</strong> ${report.report_reason}</p>
  
          <button class="btn btn-outline-warning btn-sm me-2" onclick="adminSetReviewed(${report.id})">Set Reviewed</button>
          <button class="btn btn-outline-success btn-sm me-2" onclick="adminSetResolved(${report.id})">Set Resolved</button>
          <button class="btn btn-outline-danger btn-sm" onclick="adminDeleteReport(${report.id})">Delete</button>
        </div>
      `;
      container.appendChild(card);
    });
  }
  
  async function adminSetReviewed(id) {
    const response = await apiPatch(`/api/reports/${id}/`, { status: "reviewed" }, true);
  
    if (!response.ok) {
      alert("Could not set report to reviewed.");
      return;
    }
  
    await loadAllReports();
  }
  
  async function adminSetResolved(id) {
    const response = await apiPatch(`/api/reports/${id}/`, { status: "resolved" }, true);
  
    if (!response.ok) {
      alert("Could not set report to resolved.");
      return;
    }
  
    await loadAllReports();
  }
  
  async function adminDeleteReport(id) {
    if (!confirm("Delete this report?")) return;
  
    const response = await apiDelete(`/api/reports/${id}/`, true);
  
    if (!response.ok) {
      alert("Could not delete report.");
      return;
    }
  
    const container = document.getElementById("adminReportsList");
    container.insertAdjacentHTML(
      "beforebegin",
      `<div id="adminSuccessMsg" class="alert alert-success mb-3">Report deleted successfully.</div>`
    );
  
    await loadAllReports();
  }