const state = {
  company: "HackerRank",
  history: JSON.parse(localStorage.getItem("triageHistory") || "[]"),
};

const views = [...document.querySelectorAll(".view")];
const navButtons = [...document.querySelectorAll("[data-nav]")];
const datasetRows = document.querySelector("#datasetRows");
const datasetStats = document.querySelector("#datasetStats");
const form = document.querySelector("#ticketForm");
const resultPanel = document.querySelector("#resultPanel");
const historyList = document.querySelector("#historyList");
const clearHistory = document.querySelector("#clearHistory");
const themeToggle = document.querySelector("#themeToggle");
const themeIcon = document.querySelector("#themeIcon");

function showView(id) {
  views.forEach((view) => view.classList.toggle("active", view.id === id));
  if (id === "datasetView") loadDataset();
  if (id === "queryView") renderHistory();
}

function setTheme(theme) {
  document.body.classList.toggle("dark", theme === "dark");
  themeIcon.textContent = theme === "dark" ? "G" : "B";
  localStorage.setItem("theme", theme);
}

function compact(text, limit = 96) {
  const clean = String(text || "").replace(/\s+/g, " ").trim();
  return clean.length > limit ? `${clean.slice(0, limit - 1)}...` : clean;
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function titleCase(value) {
  return String(value || "unknown").replaceAll("_", " ");
}

function pill(status) {
  const clean = String(status || "unknown").toLowerCase();
  return `<span class="pill ${clean}">${titleCase(clean)}</span>`;
}

function statCard(label, value, detail = "") {
  return `
    <div class="stat-card">
      <span>${label}</span>
      <strong>${value}</strong>
      <span>${detail}</span>
    </div>
  `;
}

async function loadDataset() {
  datasetRows.innerHTML = `<tr><td colspan="7">Running hybrid retrieval over the dataset...</td></tr>`;
  datasetStats.innerHTML = "";
  try {
    const response = await fetch("/api/dataset");
    const data = await response.json();
    const summary = data.summary || {};
    const status = summary.status || {};
    const companies = summary.company || {};
    const requestTypes = summary.request_type || {};

    datasetStats.innerHTML = [
      statCard("Tickets", summary.total || 0, "loaded from CSV"),
      statCard("Replied", status.replied || 0, "resource match is clear"),
      statCard("Escalated", status.escalated || 0, "human review needed"),
      statCard("Companies", Object.keys(companies).length, Object.keys(requestTypes).join(", ")),
    ].join("");

    datasetRows.innerHTML = data.rows.map((row) => `
      <tr title="${escapeHtml(compact(row.issue, 220))}">
        <td>${row.id}</td>
        <td>${escapeHtml(compact(row.company, 32))}</td>
        <td>${escapeHtml(compact(row.subject || row.issue, 80))}</td>
        <td>${pill(row.status)}</td>
        <td>${escapeHtml(titleCase(row.product_area))}</td>
        <td>${escapeHtml(titleCase(row.request_type))}</td>
        <td>${Number(row.top_score || 0).toFixed(3)}</td>
      </tr>
    `).join("");
  } catch (error) {
    datasetRows.innerHTML = `<tr><td colspan="7">Could not load dataset: ${error.message}</td></tr>`;
  }
}

function renderBestMatch(recommendations) {
  if (!recommendations || recommendations.length === 0) {
    return `<p class="response-box">No reliable support resource crossed the recommendation threshold.</p>`;
  }
  const item = recommendations[0];
  return `
    <div class="best-match-card">
      <span class="best-match-label">Best Match</span>
      <div class="evidence-head">
        <strong>${escapeHtml(item.title)}</strong>
        <span>${Number(item.score || 0).toFixed(3)}</span>
      </div>
      <p>${escapeHtml(compact(item.source_path, 100))}</p>
      <p>L ${Number(item.lexical_score || 0).toFixed(2)} / S ${Number(item.semantic_score || 0).toFixed(2)} / R ${Number(item.rerank_score || 0).toFixed(2)}</p>
      <p>${escapeHtml(compact(item.match_explanation, 160))}</p>
    </div>
  `;
}

function renderOtherRecs(recommendations) {
  if (!recommendations || recommendations.length <= 1) return "";
  const others = recommendations.slice(1, 3);
  return `
    <div class="other-recs">
      <h3>Other Recommendations</h3>
      <div class="evidence-list">
        ${others.map((item) => `
          <div class="evidence-item">
            <div class="evidence-head">
              <strong>#${item.rank} ${escapeHtml(item.title)}</strong>
              <span>${Number(item.score || 0).toFixed(3)}</span>
            </div>
            <p>${escapeHtml(compact(item.source_path, 74))}</p>
            <p>L ${Number(item.lexical_score || 0).toFixed(2)} / S ${Number(item.semantic_score || 0).toFixed(2)} / R ${Number(item.rerank_score || 0).toFixed(2)}</p>
            <p>${escapeHtml(compact(item.match_explanation, 130))}</p>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}

function renderTrace(trace) {
  if (!trace) return "";
  const top = trace.top_resource;
  const tokens = (trace.top_lexical_attribution || [])
    .map((item) => `${escapeHtml(item.token)} ${Number(item.weight || 0).toFixed(2)}`)
    .join(", ");
  return `
    <div class="trace-box">
      <h3>Decision Trace</h3>
      <div class="result-grid trace-grid">
        <div class="kv"><span>Rule Type</span><strong>${escapeHtml(titleCase(trace.request_type_rule))}</strong></div>
        <div class="kv"><span>Area Model</span><strong>${escapeHtml(titleCase(trace.product_area))}</strong></div>
        <div class="kv"><span>Area Prob.</span><strong>${Number(trace.area_probability || 0).toFixed(3)}</strong></div>
        <div class="kv"><span>Ambiguity Gap</span><strong>${trace.ambiguity_gap === null || trace.ambiguity_gap === undefined ? "n/a" : Number(trace.ambiguity_gap).toFixed(3)}</strong></div>
      </div>
      ${top ? `<p><strong>${escapeHtml(top.title)}</strong></p>` : ""}
      <p>Tokens: ${tokens || "semantic/reranker match"}</p>
      <p>Reason: ${escapeHtml(trace.routing_reason)}</p>
    </div>
  `;
}

function renderAiSummary(summary) {
  if (!summary) return "";
  return `
    <div class="ai-summary">
      <h3>AI Summary (Groq)</h3>
      <p>${escapeHtml(summary)}</p>
    </div>
  `;
}

function renderResult(data) {
  const prediction = data.prediction;
  const analysis = data.analysis;
  const trace = analysis.decision_trace;
  resultPanel.classList.remove("empty");
  resultPanel.innerHTML = `
    <div class="result-hero">
      <div>
        <p class="eyebrow">Recommendation output</p>
        <h3>${pill(prediction.status)} ${titleCase(prediction.product_area)}</h3>
      </div>
      <strong>${Number(analysis.top_score || 0).toFixed(3)}</strong>
    </div>
    <div class="result-grid">
      <div class="kv"><span>Type</span><strong>${escapeHtml(titleCase(prediction.request_type))}</strong></div>
      <div class="kv"><span>Confidence</span><strong>${escapeHtml(titleCase(analysis.confidence))}</strong></div>
      <div class="kv"><span>Area Prob.</span><strong>${escapeHtml(titleCase(analysis.area_confidence))}</strong></div>
      <div class="kv"><span>Resources</span><strong>${analysis.evidence_count}</strong></div>
    </div>
    <div class="result-layout">
      ${renderBestMatch(data.recommendations)}
      <section class="result-card answer-card">
        <h3>Source Response</h3>
        <p>${escapeHtml(prediction.response)}</p>
      </section>
      ${renderAiSummary(data.ai_summary)}
      <section class="result-card trace-card">
        ${renderTrace(trace)}
      </section>
      ${renderOtherRecs(data.recommendations)}
    </div>
  `;
}

function saveHistory(data) {
  const entry = {
    time: new Date().toLocaleString(),
    company: data.ticket.company,
    subject: data.ticket.subject,
    issue: data.ticket.issue,
    status: data.prediction.status,
    product_area: data.prediction.product_area,
    request_type: data.prediction.request_type,
    top_score: data.analysis.top_score,
  };
  state.history = [entry, ...state.history].slice(0, 20);
  localStorage.setItem("triageHistory", JSON.stringify(state.history));
  renderHistory();
}

function renderHistory() {
  if (!state.history.length) {
    historyList.innerHTML = `<div class="history-item"><strong>No session tickets yet</strong><p>New triage runs appear here without touching the CSV files.</p></div>`;
    return;
  }
  historyList.innerHTML = state.history.map((item) => `
    <div class="history-item">
      <strong>${escapeHtml(compact(item.subject || item.issue, 68))}</strong>
      <p>${escapeHtml(item.time)} | ${escapeHtml(item.company)} | ${pill(item.status)} | ${escapeHtml(titleCase(item.request_type))}</p>
      <p>${escapeHtml(titleCase(item.product_area))} | score ${Number(item.top_score || 0).toFixed(3)}</p>
    </div>
  `).join("");
}

navButtons.forEach((button) => {
  button.addEventListener("click", () => showView(button.dataset.nav));
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const subject = document.querySelector("#subjectInput").value;
  const issue = document.querySelector("#issueInput").value;
  resultPanel.classList.remove("empty");
  resultPanel.innerHTML = `<p class="eyebrow">Recommendation output</p><h3>Running hybrid retrieval...</h3>`;
  try {
    const response = await fetch("/api/triage", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ company: state.company, subject, issue }),
    });
    if (!response.ok) throw new Error(`Request failed with ${response.status}`);
    const data = await response.json();
    renderResult(data);
    saveHistory(data);
  } catch (error) {
    resultPanel.innerHTML = `<p class="eyebrow">Recommendation output</p><h3>Could not run triage</h3><p>${error.message}</p>`;
  }
});

clearHistory.addEventListener("click", () => {
  state.history = [];
  localStorage.removeItem("triageHistory");
  renderHistory();
});

themeToggle.addEventListener("click", () => {
  const next = document.body.classList.contains("dark") ? "light" : "dark";
  setTheme(next);
});

setTheme(localStorage.getItem("theme") || "light");
renderHistory();
