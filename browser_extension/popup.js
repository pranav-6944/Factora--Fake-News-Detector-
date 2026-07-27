/**
 * FacTora Browser Extension – Popup Script
 * Calls the FacTora local API and renders credibility results.
 */

const DEPLOYED_URL = '';  // Set your Render URL here, e.g. 'https://factora.onrender.com'
const API_BASE = DEPLOYED_URL || 'http://localhost:5000';

const headlineInput = document.getElementById('headlineInput');
const sourceUrl     = document.getElementById('sourceUrl');
const analyzeBtn    = document.getElementById('analyzeBtn');
const grabBtn       = document.getElementById('grabBtn');
const statusMsg     = document.getElementById('statusMsg');
const resultCard    = document.getElementById('resultCard');
const serverWarning = document.getElementById('serverWarning');
const charCount     = document.getElementById('charCount');

// Char counter
headlineInput.addEventListener('input', () => {
  charCount.textContent = headlineInput.value.length;
});

// Grab headline from active tab's <h1> via content script
grabBtn.addEventListener('click', async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    const result = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => {
        const h = document.querySelector('h1');
        return h ? h.innerText.trim().slice(0, 400) : '';
      }
    });
    const text = result?.[0]?.result || '';
    if (text) {
      headlineInput.value = text;
      charCount.textContent = text.length;
      // Also pre-fill the source URL
      if (!sourceUrl.value) sourceUrl.value = tab.url || '';
    } else {
      showStatus('No <h1> headline found on this page.', 'warn');
    }
  } catch (e) {
    showStatus('Cannot access this page.', 'error');
  }
});

// Analyze
analyzeBtn.addEventListener('click', runAnalysis);
headlineInput.addEventListener('keydown', (e) => {
  if (e.ctrlKey && e.key === 'Enter') runAnalysis();
});

async function runAnalysis() {
  const text = headlineInput.value.trim();
  if (!text) {
    showStatus('Please enter a headline first.', 'warn');
    return;
  }
  if (text.length < 5) {
    showStatus('Headline too short (min 5 characters).', 'warn');
    return;
  }

  setLoading(true);
  resultCard.style.display  = 'none';
  serverWarning.style.display = 'none';
  showStatus('<i class="fas fa-spinner fa-spin"></i> Analyzing with AI…');

  try {
    const resp = await fetch(`${API_BASE}/api/credibility-score`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({
        headline:   text,
        source_url: sourceUrl.value.trim() || null,
      }),
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.error || `Server error ${resp.status}`);
    }

    const data = await resp.json();
    renderResult(data);
    hideStatus();

  } catch (e) {
    if (e.message.includes('Failed to fetch') || e.message.includes('NetworkError')) {
      serverWarning.style.display = 'flex';
      hideStatus();
    } else {
      showStatus(`Error: ${e.message}`, 'error');
    }
  } finally {
    setLoading(false);
  }
}

function renderResult(d) {
  const score   = d.credibility_score || 0;
  const grade   = d.grade || '?';
  const verdict = d.verdict || 'UNKNOWN';
  const factors = d.factors || {};

  // Verdict banner
  const banner = document.getElementById('verdictBanner');
  const icon   = document.getElementById('verdictIcon');
  const label  = document.getElementById('verdictLabel');
  const sub    = document.getElementById('verdictSub');
  if (verdict === 'REAL') {
    banner.className = 'ext-verdict real';
    icon.textContent = '✅';
    label.textContent = 'Likely REAL';
    label.style.color = '#4ade80';
  } else {
    banner.className = 'ext-verdict fake';
    icon.textContent = '🚨';
    label.textContent = 'Likely FAKE';
    label.style.color = '#f87171';
  }
  sub.textContent = `${d.bert_confidence?.toFixed(1) ?? '—'}% AI confidence`;

  // Gauge arc (SVG)
  const arc   = document.getElementById('gaugeArc');
  const total = 172.8; // half-circle circumference for r=55
  const offset = total - (score / 100) * total;
  arc.style.strokeDashoffset = offset;
  arc.style.stroke = scoreColor(score);
  document.getElementById('gaugeScore').textContent = score.toFixed(0);

  // Grade
  document.getElementById('gradeSpan').textContent  = grade;
  document.getElementById('gradeLabel').textContent  = d.label || '';
  document.getElementById('gradeSpan').style.background = d.color || '#374151';
  document.getElementById('gradeSpan').style.color = '#fff';

  // Factor bars
  setFactor('barBert', 'valBert', factors.bert?.score ?? 0);
  setFactor('barLing', 'valLing', factors.linguistic?.score ?? 0);
  setFactor('barSrc',  'valSrc',  factors.source?.score ?? 0);

  // Linguistic signals
  const signals = factors.linguistic?.signals || [];
  const signalsList = document.getElementById('signalsList');
  if (signals.length > 0) {
    signalsList.innerHTML = signals.map(s => `<span class="ext-signal-pill">${s}</span>`).join('');
    signalsList.style.display = 'flex';
  } else {
    signalsList.style.display = 'none';
  }

  // Badges
  const badges = document.getElementById('extBadges');
  badges.innerHTML = '';
  const srcTrustLevel = factors.source?.trust_level || 'unknown';
  badges.innerHTML += `<span class="ext-badge ext-badge-${srcTrustLevel}">${factors.source?.badge || '❓ Source'}</span>`;
  if (factors.linguistic?.clickbait) {
    badges.innerHTML += `<span class="ext-badge ext-badge-clickbait">⚠ Clickbait</span>`;
  }
  if (factors.linguistic?.conspiracy) {
    badges.innerHTML += `<span class="ext-badge ext-badge-conspiracy">🔴 Conspiracy</span>`;
  }

  // Open link — pass headline as query
  const q = encodeURIComponent(headlineInput.value.trim().slice(0, 200));
  document.getElementById('openFacTora').href = `http://localhost:5000/?q=${q}`;

  resultCard.style.display = 'flex';
}

function setFactor(barId, valId, score) {
  document.getElementById(barId).style.width = score + '%';
  document.getElementById(valId).textContent  = score.toFixed(0);
  const bar = document.getElementById(barId);
  if (score >= 70) bar.style.background = 'linear-gradient(90deg,#22c55e,#4ade80)';
  else if (score >= 45) bar.style.background = 'linear-gradient(90deg,#eab308,#facc15)';
  else bar.style.background = 'linear-gradient(90deg,#ef4444,#f87171)';
}

function scoreColor(s) {
  if (s >= 70) return '#22c55e';
  if (s >= 50) return '#eab308';
  return '#ef4444';
}

function setLoading(on) {
  analyzeBtn.disabled = on;
  document.getElementById('btnText').textContent = on ? 'Analyzing…' : 'Analyze';
}

function showStatus(html, type = 'info') {
  statusMsg.innerHTML = html;
  statusMsg.style.display = 'flex';
  statusMsg.style.color = type === 'error' ? '#f87171' : type === 'warn' ? '#facc15' : 'rgba(255,255,255,.5)';
}
function hideStatus() {
  statusMsg.style.display = 'none';
}
