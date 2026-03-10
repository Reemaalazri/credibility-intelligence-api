let editingReportId = null;
let currentReports = [];

document.addEventListener("DOMContentLoaded", () => {
  updateNavbar();
  bindLogoutButtons();

  if (!getAccessToken()) {
    document.getElementById("reportsResult").innerHTML =
      `<div class="alert alert-danger">Please log in first.</div>`;
    return;
  }

  document.getElementById("reportForm").addEventListener("submit", handleReportSubmit);
  loadMyReports();
});

async function handleReportSubmit(e) {
  e.preventDefault();

  const payload = {
    statement_text: document.getElementById("statement_text").value.trim(),
    speaker: document.getElementById("speaker").value.trim(),
    report_reason: document.getElementById("report_reason").value.trim(),
    risk_score: parseFloat(document.getElementById("risk_score").value || "0"),
    risk_level: document.getElementById("risk_level").value
  };

  let response;
  let successMessage;

  if (editingReportId) {
    response = await apiPatch(`/api/reports/${editingReportId}/`, payload, true);
    successMessage = "Report updated successfully.";
  } else {
    response = await apiPost("/api/reports/", payload, true);
    successMessage = "Report created successfully.";
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    document.getElementById("reportsResult").innerHTML =
      `<div class="alert alert-danger">${data.detail || data.error || "Could not save report."}</div>`;
    return;
  }

  document.getElementById("reportForm").reset();
  document.getElementById("reportsResult").innerHTML =
    `<div class="alert alert-success">${successMessage}</div>`;

  editingReportId = null;
  updateFormMode();
  await loadMyReports();
}

async function loadMyReports() {
  const container = document.getElementById("myReportsList");
  container.innerHTML = `<div class="alert alert-info">Loading reports...</div>`;

  const response = await apiGet("/api/reports/", true);

  if (!response.ok) {
    container.innerHTML = `<div class="alert alert-danger">Could not load reports.</div>`;
    return;
  }

  const data = await response.json();
  const reports = data.results || [];
  currentReports = reports;

  if (!reports.length) {
    container.innerHTML = `<div class="alert alert-warning">No reports found.</div>`;
    return;
  }

  container.innerHTML = "";

  reports.forEach(report => {
    const card = document.createElement("div");
    card.className = "card report-card shadow-sm";
    card.innerHTML = `
      <div class="card-body">
        <h5 class="card-title">${report.statement_text}</h5>
        <p class="mb-1"><strong>Speaker:</strong> ${report.speaker || "Unknown"}</p>
        <p class="mb-1"><strong>Reason:</strong> ${report.report_reason || "N/A"}</p>
        <p class="mb-1"><strong>Risk Score:</strong> ${report.risk_score}</p>
        <p class="mb-1"><strong>Risk Level:</strong> ${report.risk_level}</p>
        <p class="mb-2"><strong>Status:</strong> ${report.status}</p>

        <button class="btn btn-outline-primary btn-sm me-2" onclick="editReport(${report.id})">Edit</button>
        <button class="btn btn-outline-danger btn-sm" onclick="deleteReport(${report.id})">Delete</button>
      </div>
    `;
    container.appendChild(card);
  });
}

function editReport(id) {
  const report = currentReports.find(r => r.id === id);
  if (!report) return;

  editingReportId = id;

  document.getElementById("statement_text").value = report.statement_text || "";
  document.getElementById("speaker").value = report.speaker || "";
  document.getElementById("report_reason").value = report.report_reason || "";
  document.getElementById("risk_score").value = report.risk_score ?? 0;
  document.getElementById("risk_level").value = report.risk_level || "unknown";

  updateFormMode();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function updateFormMode() {
  const submitBtn = document.getElementById("reportSubmitBtn");
  const cancelBtn = document.getElementById("cancelEditBtn");

  if (editingReportId) {
    submitBtn.textContent = "Update Report";
    submitBtn.className = "btn btn-primary";
    cancelBtn.classList.remove("hidden");
  } else {
    submitBtn.textContent = "Submit Report";
    submitBtn.className = "btn btn-success";
    cancelBtn.classList.add("hidden");
  }
}

function cancelEdit() {
  editingReportId = null;
  document.getElementById("reportForm").reset();
  updateFormMode();
}

async function deleteReport(id) {
    if (!confirm("Delete this report?")) return;
  
    const response = await apiDelete(`/api/reports/${id}/`, true);
  
    if (!response.ok) {
      document.getElementById("reportsResult").innerHTML =
        `<div class="alert alert-danger">Could not delete the report.</div>`;
      return;
    }
  
    if (editingReportId === id) {
      cancelEdit();
    }
  
    document.getElementById("reportsResult").innerHTML =
      `<div class="alert alert-success">Report deleted successfully.</div>`;
  
    await loadMyReports();
}