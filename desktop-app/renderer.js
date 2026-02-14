const { ipcRenderer } = require('electron');

let isOn = false;
let isExpanded = false;
const body = document.body;
const launcherBtn = document.getElementById('launcher');
const collapseBtn = document.getElementById('collapse');
const panel = document.getElementById('panel');
const toggleBtn = document.getElementById('toggle');
const resultDiv = document.getElementById('result');

function inferThreatLevel(data) {
  if (!data || typeof data !== 'object') return "UNKNOWN";

  // Prefer canonical /analyze response fields first.
  if (typeof data.severity === "string" && data.severity.trim()) {
    return data.severity.toUpperCase();
  }

  if (typeof data.overall_risk === "number") {
    const score = data.overall_risk;
    if (score < 30) return "LOW";
    if (score < 60) return "MEDIUM";
    if (score < 85) return "HIGH";
    return "CRITICAL";
  }

  // /analyze_text style fields (risk_score can be 0..1 or 0..100).
  if (typeof data.risk_score === "number") {
    const score = data.risk_score <= 1 ? data.risk_score * 100 : data.risk_score;
    if (score <= 30) return "SAFE";
    if (score <= 55) return "SUSPICIOUS";
    if (score <= 80) return "HIGH RISK";
    return "CRITICAL";
  }

  if (typeof data.risk_level === "string" && data.risk_level.trim()) {
    return data.risk_level.toUpperCase();
  }

  if (typeof data.result === "string" && data.result.trim()) {
    return data.result.toUpperCase();
  }

  return "UNKNOWN";
}

function inferThreatScore(data) {
  if (!data || typeof data !== 'object') return 0;
  if (typeof data.threat_score === "number") return Math.max(0, Math.min(100, Math.round(data.threat_score)));
  if (typeof data.overall_risk === "number") return Math.max(0, Math.min(100, Math.round(data.overall_risk)));
  if (typeof data.risk_score === "number") {
    const score = data.risk_score <= 1 ? data.risk_score * 100 : data.risk_score;
    return Math.max(0, Math.min(100, Math.round(score)));
  }
  return 0;
}

function renderAnalysis(data) {
  const threatLevel = inferThreatLevel(data);
  const threatScore = inferThreatScore(data);
  const scannedBlocks = typeof data.scanned_blocks === "number" ? data.scanned_blocks : 1;
  const detectedLanguage = (data.detected_language || "Unknown").toString();

  const manipulationRadars = Array.isArray(data.manipulation_radars) ? data.manipulation_radars : [];
  const technicalIndicators = Array.isArray(data.technical_indicators) ? data.technical_indicators : [];
  const suspiciousDomains = Array.isArray(data.suspicious_domains) ? data.suspicious_domains : [];

  resultDiv.innerHTML = `
    <div><strong>Threat Level:</strong> ${threatLevel}</div>
    <div><strong>Threat Score:</strong> ${threatScore}/100</div>
    <div><strong>Scanned Blocks:</strong> ${scannedBlocks}</div>
    <div><strong>Detected Language:</strong> ${detectedLanguage}</div>
    <div style="margin-top:8px;"><strong>Manipulation Radar:</strong> ${manipulationRadars.length ? manipulationRadars.join(", ") : "None detected"}</div>
    <div style="margin-top:6px;"><strong>Technical Indicators:</strong> ${technicalIndicators.length ? technicalIndicators.join(", ") : "None detected"}</div>
    <div style="margin-top:6px;"><strong>Suspicious Domains:</strong> ${suspiciousDomains.length ? suspiciousDomains.join(", ") : "None detected"}</div>
  `;
}

function setExpandedState(nextState) {
  isExpanded = nextState;
  body.classList.toggle('expanded', isExpanded);
  launcherBtn.style.display = isExpanded ? 'none' : 'block';
  panel.style.display = isExpanded ? 'block' : 'none';
  ipcRenderer.send('set-window-state', isExpanded);
}

launcherBtn.addEventListener('click', () => {
  setExpandedState(true);
});

collapseBtn.addEventListener('click', () => {
  setExpandedState(false);
});

toggleBtn.addEventListener('click', () => {
  isOn = !isOn;
  toggleBtn.innerText = isOn ? "ON" : "OFF";
  toggleBtn.style.background = isOn ? "green" : "red";
});

ipcRenderer.on('analyze-text', async (event, text) => {
  if (!isOn || !text) return;

  resultDiv.innerText = "Analyzing...";

  try {
    const payload = JSON.stringify({ text: text });
    const headers = { "Content-Type": "application/json" };

    let response = await fetch("http://127.0.0.1:8000/analyze", {
      method: "POST",
      headers: headers,
      body: payload
    });

    // Compatibility: some backend variants expose /analyze_text instead of /analyze.
    if (response.status === 404) {
      response = await fetch("http://127.0.0.1:8000/analyze_text", {
        method: "POST",
        headers: headers,
        body: payload
      });
    }

    if (!response.ok) {
      throw new Error("Backend error: " + response.status);
    }

    const data = await response.json();
    renderAnalysis(data);

  } catch (err) {
    resultDiv.innerText = "Backend not running!";
  }
});

window.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && isExpanded) {
    setExpandedState(false);
  }
});

setExpandedState(false);
