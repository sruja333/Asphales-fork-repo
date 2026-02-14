const { ipcRenderer } = require('electron');

let isOn = true;
let isExpanded = false;
let selectedLanguage = 'en';
let lastAnalysisData = null;
let renderSequence = 0;

const body = document.body;
const launcherBtn = document.getElementById('launcher');
const collapseBtn = document.getElementById('collapse');
const panel = document.getElementById('panel');
const toggleBtn = document.getElementById('toggle');
const speakBtn = document.getElementById('speak-summary');
const themeBtn = document.getElementById('theme-toggle');
const resultDiv = document.getElementById('result');
const languageSelect = document.getElementById('language-select');
const languageLabel = document.querySelector('label[for="language-select"]');

const LANGUAGE_OPTIONS = [
  { code: 'en', label: 'English' },
  { code: 'as', label: 'Assamese' },
  { code: 'bn', label: 'Bengali' },
  { code: 'brx', label: 'Bodo' },
  { code: 'doi', label: 'Dogri' },
  { code: 'gu', label: 'Gujarati' },
  { code: 'hi', label: 'Hindi' },
  { code: 'kn', label: 'Kannada' },
  { code: 'ks', label: 'Kashmiri' },
  { code: 'gom', label: 'Konkani' },
  { code: 'mai', label: 'Maithili' },
  { code: 'ml', label: 'Malayalam' },
  { code: 'mni', label: 'Manipuri' },
  { code: 'mr', label: 'Marathi' },
  { code: 'ne', label: 'Nepali' },
  { code: 'or', label: 'Odia' },
  { code: 'pa', label: 'Punjabi' },
  { code: 'sa', label: 'Sanskrit' },
  { code: 'sat', label: 'Santali' },
  { code: 'sd', label: 'Sindhi' },
  { code: 'ta', label: 'Tamil' },
  { code: 'te', label: 'Telugu' },
  { code: 'ur', label: 'Urdu' }
];

const TRANSLATE_TARGET_MAP = {
  en: 'en',
  as: 'as',
  bn: 'bn',
  brx: 'hi',
  doi: 'hi',
  gu: 'gu',
  hi: 'hi',
  kn: 'kn',
  ks: 'ur',
  gom: 'hi',
  mai: 'hi',
  ml: 'ml',
  mni: 'hi',
  mr: 'mr',
  ne: 'ne',
  or: 'or',
  pa: 'pa',
  sa: 'sa',
  sat: 'hi',
  sd: 'sd',
  ta: 'ta',
  te: 'te',
  ur: 'ur'
};

const TTS_LANG_MAP = {
  en: 'en-IN',
  as: 'as-IN',
  bn: 'bn-IN',
  brx: 'hi-IN',
  doi: 'hi-IN',
  gu: 'gu-IN',
  hi: 'hi-IN',
  kn: 'kn-IN',
  ks: 'ur-IN',
  gom: 'hi-IN',
  mai: 'hi-IN',
  ml: 'ml-IN',
  mni: 'hi-IN',
  mr: 'mr-IN',
  ne: 'ne-NP',
  or: 'or-IN',
  pa: 'pa-IN',
  sa: 'hi-IN',
  sat: 'hi-IN',
  sd: 'sd-IN',
  ta: 'ta-IN',
  te: 'te-IN',
  ur: 'ur-IN'
};

const translationCache = new Map();
let audioPlayer = null;
let cachedVoices = [];
let voicesReady = false;

function getTranslateTarget() {
  return TRANSLATE_TARGET_MAP[selectedLanguage] || 'en';
}

function getSpeechLang() {
  return TTS_LANG_MAP[selectedLanguage] || 'en-IN';
}

function cacheKey(languageCode, text) {
  return `${languageCode}::${text}`;
}

async function translateText(text) {
  const raw = String(text || '');
  if (!raw.trim()) return raw;

  const target = getTranslateTarget();
  if (target === 'en') return raw;

  const key = cacheKey(target, raw);
  if (translationCache.has(key)) {
    return translationCache.get(key);
  }

  try {
    const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=${encodeURIComponent(target)}&dt=t&q=${encodeURIComponent(raw)}`;
    const response = await fetch(url);
    if (!response.ok) {
      translationCache.set(key, raw);
      return raw;
    }

    const payload = await response.json();
    const translated = Array.isArray(payload?.[0])
      ? payload[0].map((part) => (Array.isArray(part) ? part[0] : '')).join('')
      : raw;

    const normalized = translated || raw;
    translationCache.set(key, normalized);
    return normalized;
  } catch {
    translationCache.set(key, raw);
    return raw;
  }
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function inferThreatLevel(data) {
  if (!data || typeof data !== 'object') return 'UNKNOWN';

  if (typeof data.severity === 'string' && data.severity.trim()) {
    return data.severity.toUpperCase();
  }

  if (typeof data.overall_risk === 'number') {
    const score = data.overall_risk;
    if (score < 30) return 'LOW';
    if (score < 60) return 'MEDIUM';
    if (score < 85) return 'HIGH';
    return 'CRITICAL';
  }

  if (typeof data.risk_score === 'number') {
    const score = data.risk_score <= 1 ? data.risk_score * 100 : data.risk_score;
    if (score <= 30) return 'SAFE';
    if (score <= 55) return 'SUSPICIOUS';
    if (score <= 80) return 'HIGH RISK';
    return 'CRITICAL';
  }

  if (typeof data.risk_level === 'string' && data.risk_level.trim()) {
    return data.risk_level.toUpperCase();
  }

  if (typeof data.result === 'string' && data.result.trim()) {
    return data.result.toUpperCase();
  }

  return 'UNKNOWN';
}

function inferThreatScore(data) {
  if (!data || typeof data !== 'object') return 0;
  if (typeof data.threat_score === 'number') return Math.max(0, Math.min(100, Math.round(data.threat_score)));
  if (typeof data.overall_risk === 'number') return Math.max(0, Math.min(100, Math.round(data.overall_risk)));
  if (typeof data.risk_score === 'number') {
    const score = data.risk_score <= 1 ? data.risk_score * 100 : data.risk_score;
    return Math.max(0, Math.min(100, Math.round(score)));
  }
  return 0;
}

function normalizeStringList(value) {
  if (Array.isArray(value)) {
    return value
      .map((item) => String(item || '').trim())
      .filter(Boolean);
  }

  if (typeof value === 'string') {
    return value
      .split(/[,;\n|]+/)
      .map((item) => item.trim())
      .filter(Boolean);
  }

  return [];
}

function uniqueValues(items) {
  return [...new Set(items)];
}

function safeTitleCase(text) {
  return String(text || '')
    .replace(/[_-]+/g, ' ')
    .trim()
    .replace(/\w\S*/g, (word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase());
}

function extractDomainsFromLinks(links) {
  const domains = [];
  const candidates = normalizeStringList(links);

  for (const link of candidates) {
    try {
      const parsed = new URL(link);
      if (parsed.hostname) {
        domains.push(parsed.hostname.toLowerCase());
      }
    } catch {
      // Ignore malformed links from backend.
    }
  }

  return uniqueValues(domains);
}

function resolveDetectedLanguage(data) {
  const candidate =
    data.detected_language ??
    data.detected_languages ??
    data.language ??
    data.lang ??
    'Unknown';

  if (Array.isArray(candidate)) {
    const normalized = normalizeStringList(candidate);
    return normalized.length ? normalized.join(', ') : 'Unknown';
  }

  const asText = String(candidate || '').trim();
  return asText || 'Unknown';
}

function resolveManipulationRadars(data) {
  let radars = normalizeStringList(data.manipulation_radars || data.manipulation_radar);

  if (!radars.length) {
    radars = normalizeStringList(data.genai_validation?.tactics);
  }

  if (!radars.length) {
    radars = normalizeStringList(data.detected_signals).map((signal) => safeTitleCase(signal));
  }

  return uniqueValues(radars);
}

function resolveTechnicalIndicators(data) {
  let indicators = normalizeStringList(data.technical_indicators || data.technical_indicator);

  if (!indicators.length) {
    indicators = normalizeStringList(data.structured_explanation?.technical_indicators);
  }

  if (!indicators.length && normalizeStringList(data.links).length) {
    indicators = ['External link present'];
  }

  return uniqueValues(indicators);
}

function resolveSuspiciousDomains(data) {
  let domains = normalizeStringList(data.suspicious_domains || data.suspicious_domain);

  if (!domains.length) {
    domains = extractDomainsFromLinks(data.links);
  } else {
    domains = domains.map((entry) => {
      const raw = String(entry).trim();
      try {
        const parsed = new URL(raw);
        return parsed.hostname.toLowerCase();
      } catch {
        return raw.toLowerCase();
      }
    });
  }

  return uniqueValues(domains);
}

function buildEasySummaryEnglish(data) {
  const rawLevel = inferThreatLevel(data);
  let spokenLevel = 'HIGH';

  if (rawLevel === 'LOW' || rawLevel === 'SAFE') {
    spokenLevel = 'LOW';
  } else if (rawLevel === 'MEDIUM' || rawLevel === 'SUSPICIOUS') {
    spokenLevel = 'MEDIUM';
  }

  let guidance = 'Message is suspicious, proceed with caution.';
  if (spokenLevel === 'LOW') {
    guidance = 'Message is safe.';
  } else if (spokenLevel === 'HIGH') {
    guidance = 'Message is risky, ignore it.';
  }

  return [
    `Threat level is ${spokenLevel}.`,
    guidance
  ].join(' ');
}

function pickBestVoice(voices, langCode) {
  if (!voices.length) return null;

  const exact = voices.find((voice) => (voice.lang || '').toLowerCase() === langCode.toLowerCase());
  if (exact) return exact;

  const base = langCode.split('-')[0].toLowerCase();
  const baseMatch = voices.find((voice) => (voice.lang || '').toLowerCase().startsWith(base));
  if (baseMatch) return baseMatch;

  const indianEnglish = voices.find((voice) => (voice.lang || '').toLowerCase() === 'en-in');
  if (indianEnglish) return indianEnglish;

  return voices.find((voice) => voice.default) || voices[0];
}

function refreshVoices() {
  if (!window.speechSynthesis) return [];
  cachedVoices = window.speechSynthesis.getVoices() || [];
  voicesReady = true;
  return cachedVoices;
}

function hasVoiceForLang(voices, langCode) {
  if (!voices.length) return false;
  const normalized = langCode.toLowerCase();
  if (voices.some((voice) => (voice.lang || '').toLowerCase() === normalized)) return true;
  const base = normalized.split('-')[0];
  return voices.some((voice) => (voice.lang || '').toLowerCase().startsWith(base));
}

function speakWithSystemVoice(text) {
  const synth = window.speechSynthesis;
  if (!synth || typeof SpeechSynthesisUtterance === 'undefined') return;

  const utterance = new SpeechSynthesisUtterance(text);
  const lang = getSpeechLang();
  utterance.lang = lang;
  utterance.rate = 0.92;
  utterance.pitch = 1;
  utterance.volume = 1;

  const voices = voicesReady ? cachedVoices : refreshVoices();
  const selectedVoice = pickBestVoice(voices, lang);
  if (selectedVoice) {
    utterance.voice = selectedVoice;
  }

  synth.cancel();
  synth.speak(utterance);
}

async function tryRemoteTts(text, targetLang) {
  try {
    const capped = String(text || '').slice(0, 190);
    const url = `https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=${encodeURIComponent(targetLang)}&q=${encodeURIComponent(capped)}`;

    if (audioPlayer) {
      audioPlayer.pause();
      audioPlayer = null;
    }

    audioPlayer = new Audio(url);
    audioPlayer.crossOrigin = 'anonymous';
    audioPlayer.volume = 1;
    await audioPlayer.play();
    return true;
  } catch {
    return false;
  }
}

async function speakText(text) {
  const payload = String(text || '').trim();
  if (!payload) return;

  const target = getTranslateTarget();
  const systemLang = getSpeechLang();
  const voices = voicesReady ? cachedVoices : refreshVoices();
  const hasSystemVoice = hasVoiceForLang(voices, systemLang);

  if (hasSystemVoice) {
    speakWithSystemVoice(payload);
    return;
  }

  if (target !== 'en') {
    const played = await tryRemoteTts(payload, target);
    if (played) return;
  }

  speakWithSystemVoice(payload);
}

async function speakLatestSummary() {
  if (!lastAnalysisData) {
    const noDataText = await translateText('No analysis available yet. Please scan text first.');
    resultDiv.innerText = noDataText;
    await speakText(noDataText);
    return;
  }

  const englishSummary = buildEasySummaryEnglish(lastAnalysisData);
  const translatedSummary = await translateText(englishSummary);
  await speakText(translatedSummary);
}

async function updateLanguageLabel() {
  languageLabel.textContent = await translateText('Display Language');
  const speakLabel = await translateText('Speak summary');
  speakBtn.title = speakLabel;
  speakBtn.setAttribute('aria-label', speakLabel);
  await updateThemeButtonText();
}

function applyTheme(themeMode) {
  const next = themeMode === 'dark' ? 'dark' : 'light';
  body.classList.toggle('dark', next === 'dark');
  localStorage.setItem('suraksha-theme', next);
}

function syncToggleState() {
  toggleBtn.innerText = isOn ? 'ON' : 'OFF';
  toggleBtn.style.background = isOn ? 'green' : 'red';
}

async function updateThemeButtonText() {
  const isDark = body.classList.contains('dark');
  themeBtn.textContent = isDark ? '\u2600\uFE0F' : '\uD83C\uDF19';
  const tooltip = await translateText('Toggle theme');
  themeBtn.title = tooltip;
  themeBtn.setAttribute('aria-label', tooltip);
}


function populateLanguageSelector() {
  for (const option of LANGUAGE_OPTIONS) {
    const element = document.createElement('option');
    element.value = option.code;
    element.textContent = option.label;
    if (option.code === 'en') element.selected = true;
    languageSelect.appendChild(element);
  }

  languageSelect.addEventListener('change', async () => {
    selectedLanguage = languageSelect.value;
    await updateLanguageLabel();

    if (lastAnalysisData) {
      await renderAnalysis(lastAnalysisData);
    }
  });
}

async function renderAnalysis(data) {
  lastAnalysisData = data;
  const currentRender = ++renderSequence;

  const threatLevel = inferThreatLevel(data);
  const threatScore = inferThreatScore(data);
  const detectedLanguage = resolveDetectedLanguage(data);
  const manipulationRadars = resolveManipulationRadars(data);
  const technicalIndicators = resolveTechnicalIndicators(data);
  const suspiciousDomains = resolveSuspiciousDomains(data);

  const manipulationText = manipulationRadars.length ? manipulationRadars.join(', ') : 'None detected';
  const technicalText = technicalIndicators.length ? technicalIndicators.join(', ') : 'None detected';
  const domainsText = suspiciousDomains.length ? suspiciousDomains.join(', ') : 'None detected';

  const [
    threatLevelLabel,
    threatScoreLabel,
    detectedLanguageLabel,
    manipulationRadarLabel,
    technicalIndicatorsLabel,
    suspiciousDomainsLabel,
    translatedThreatLevel,
    translatedDetectedLanguage,
    translatedNoneDetected,
    translatedManipulation,
    translatedTechnical
  ] = await Promise.all([
    translateText('Threat Level'),
    translateText('Threat Score'),
    translateText('Detected Language'),
    translateText('Manipulation Radar'),
    translateText('Technical Indicators'),
    translateText('Suspicious Domains'),
    translateText(threatLevel),
    translateText(detectedLanguage),
    translateText('None detected'),
    manipulationRadars.length ? translateText(manipulationText) : Promise.resolve(''),
    technicalIndicators.length ? translateText(technicalText) : Promise.resolve('')
  ]);

  if (currentRender !== renderSequence) return;

  const displayedManipulation = manipulationRadars.length ? translatedManipulation : translatedNoneDetected;
  const displayedTechnical = technicalIndicators.length ? translatedTechnical : translatedNoneDetected;
  const displayedDomains = suspiciousDomains.length ? domainsText : translatedNoneDetected;

  resultDiv.innerHTML = `
    <div><strong>${escapeHtml(threatLevelLabel)}:</strong> ${escapeHtml(translatedThreatLevel)}</div>
    <div><strong>${escapeHtml(threatScoreLabel)}:</strong> ${threatScore}/100</div>
    <div><strong>${escapeHtml(detectedLanguageLabel)}:</strong> ${escapeHtml(translatedDetectedLanguage)}</div>
    <div style="margin-top:8px;"><strong>${escapeHtml(manipulationRadarLabel)}:</strong> ${escapeHtml(displayedManipulation)}</div>
    <div style="margin-top:6px;"><strong>${escapeHtml(technicalIndicatorsLabel)}:</strong> ${escapeHtml(displayedTechnical)}</div>
    <div style="margin-top:6px;"><strong>${escapeHtml(suspiciousDomainsLabel)}:</strong> ${escapeHtml(displayedDomains)}</div>
  `;
  resultDiv.scrollTop = 0;
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
  syncToggleState();
});

speakBtn.addEventListener('click', async () => {
  await speakLatestSummary();
});

themeBtn.addEventListener('click', async () => {
  const nextTheme = body.classList.contains('dark') ? 'light' : 'dark';
  applyTheme(nextTheme);
  await updateThemeButtonText();
});

ipcRenderer.on('analyze-text', async (event, text) => {
  if (!isOn) return;

  const payloadText = String(text || '');
  if (!payloadText.trim()) {
    resultDiv.innerText = await translateText('No text captured. Select text and press Ctrl+C, then Ctrl+Shift+X.');
    return;
  }

  resultDiv.innerText = await translateText('Analyzing...');
  const API_BASE = (process.env.SURAKSHA_API_URL || 'https://asphales-fork-repo.onrender.com').replace(/\/$/, '');

  try {
    const payload = JSON.stringify({ text: payloadText });
    const headers = { 'Content-Type': 'application/json' };

    let response = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers,
      body: payload
    });

    if (response.status === 404) {
      response = await fetch(`${API_BASE}/analyze_text`, {
        method: 'POST',
        headers,
        body: payload
      });
    }

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    await renderAnalysis(data);
  } catch {
    resultDiv.innerText = await translateText('Backend not running!');
  }
});

window.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && isExpanded) {
    setExpandedState(false);
  }
});

if (window.speechSynthesis) {
  refreshVoices();
  window.speechSynthesis.onvoiceschanged = () => {
    refreshVoices();
  };
}

populateLanguageSelector();
applyTheme(localStorage.getItem('suraksha-theme') || 'light');
updateLanguageLabel();
setExpandedState(false);

