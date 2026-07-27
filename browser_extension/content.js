/**
 * FacTora Browser Extension – Content Script
 * Scans article headlines on any web page and adds a clickable FacTora badge.
 * On click, shows an inline credibility tooltip.
 */

const FACTORA_API = 'http://localhost:5000/api/credibility-score';
const BADGE_CLASS  = 'factora-badge';
const TOOLTIP_CLASS = 'factora-tooltip';
const PROCESSED_ATTR = 'data-factora-scanned';

// ─── Inject styles ─────────────────────────────────────────────────────────
const style = document.createElement('style');
style.textContent = `
  .factora-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-left: 7px;
    padding: 2px 8px;
    background: rgba(178,115,86,.15);
    border: 1px solid rgba(178,115,86,.4);
    border-radius: 50px;
    font-size: 0.68rem !important;
    font-family: 'Poppins', Arial, sans-serif !important;
    font-weight: 600 !important;
    color: #d4956e !important;
    cursor: pointer;
    vertical-align: middle;
    line-height: 1.4 !important;
    text-decoration: none !important;
    transition: background 0.2s, border-color 0.2s;
    white-space: nowrap;
    position: relative;
    z-index: 9990;
  }
  .factora-badge:hover {
    background: rgba(178,115,86,.28);
    border-color: rgba(212,149,110,.6);
  }
  .factora-badge.loading { color: rgba(212,149,110,.6) !important; }
  .factora-badge.real  { background:rgba(34,197,94,.12);  border-color:rgba(34,197,94,.4);  color:#4ade80 !important; }
  .factora-badge.fake  { background:rgba(239,68,68,.12);  border-color:rgba(239,68,68,.4);  color:#f87171 !important; }
  .factora-badge.error { background:rgba(255,255,255,.06); border-color:rgba(255,255,255,.15); color:rgba(255,255,255,.4) !important; }

  .factora-tooltip {
    position: fixed;
    z-index: 99999;
    background: #1a1025;
    border: 1px solid rgba(178,115,86,.35);
    border-radius: 14px;
    padding: 14px 16px;
    width: 280px;
    box-shadow: 0 20px 60px rgba(0,0,0,.5);
    font-family: 'Poppins', Arial, sans-serif;
    color: #f5f5f5;
    font-size: 12px;
    animation: factora-in .18s ease;
    pointer-events: none;
  }
  @keyframes factora-in {
    from { opacity:0; transform:translateY(-6px); }
    to   { opacity:1; transform:translateY(0); }
  }
  .factora-tooltip-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
  }
  .factora-tooltip-logo { font-size:0.8rem; font-weight:700; color:#d4956e; }
  .factora-tooltip-score {
    font-size: 1.6rem;
    font-weight: 800;
    text-align: center;
    margin: 4px 0;
  }
  .factora-tooltip-grade-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    margin-bottom: 10px;
  }
  .factora-grade {
    padding: 2px 10px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 700;
  }
  .factora-label { font-size:0.78rem; color:rgba(255,255,255,.55); }
  .factora-bar-row { display:flex; align-items:center; gap:6px; margin-bottom:4px; }
  .factora-bar-name { font-size:0.68rem; color:rgba(255,255,255,.45); width:60px; }
  .factora-bar-wrap {
    flex:1; background:rgba(255,255,255,.08);
    border-radius:50px; height:5px; overflow:hidden;
  }
  .factora-bar { height:100%; border-radius:50px; background:linear-gradient(90deg,#b37356,#d4956e); }
  .factora-bar-val { font-size:0.65rem; color:rgba(255,255,255,.4); width:20px; text-align:right; }
  .factora-source-badge {
    margin-top: 8px;
    padding: 4px 10px;
    border-radius: 50px;
    font-size: 0.7rem;
    font-weight: 500;
    display: inline-block;
    background: rgba(255,255,255,.08);
    border: 1px solid rgba(255,255,255,.12);
  }
  .factora-open-btn {
    display: block;
    margin-top: 10px;
    text-align: center;
    padding: 6px;
    background: linear-gradient(135deg,#b37356,#d4956e);
    border-radius: 8px;
    color: #fff !important;
    font-size: 0.75rem;
    font-weight: 600;
    text-decoration: none !important;
    pointer-events: all;
    cursor: pointer;
  }
`;
document.head.appendChild(style);

// ─── State ─────────────────────────────────────────────────────────────────
let activeTooltip = null;
let cacheMap = {};

// ─── Main: find and badge headlines ────────────────────────────────────────
function processHeadlines() {
  // Limit to visible article headlines only
  const selectors = [
    'h1', 'h2',
    'article h3', '.headline', '.article-title',
    '[data-testid*="headline"]', '[class*="headline"]',
    '[class*="article-title"]', '[class*="story-title"]',
  ];

  const seen = new Set();
  selectors.forEach(sel => {
    document.querySelectorAll(sel).forEach(el => {
      if (el.hasAttribute(PROCESSED_ATTR)) return;
      const text = el.innerText?.trim();
      if (!text || text.length < 10 || seen.has(text)) return;
      seen.add(text);
      el.setAttribute(PROCESSED_ATTR, '1');
      injectBadge(el, text);
    });
  });
}

function injectBadge(el, headline) {
  const badge = document.createElement('span');
  badge.className = BADGE_CLASS;
  badge.innerHTML = '🔍 FacTora';
  badge.title = 'Click to check credibility';

  badge.addEventListener('click', async (e) => {
    e.preventDefault();
    e.stopPropagation();
    removeTooltips();

    if (cacheMap[headline]) {
      showTooltip(badge, cacheMap[headline]);
      return;
    }

    badge.className = BADGE_CLASS + ' loading';
    badge.innerHTML = '⏳ Checking…';

    try {
      const resp = await fetch(FACTORA_API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ headline, source_url: window.location.href }),
      });
      if (!resp.ok) throw new Error('API error');
      const data = await resp.json();
      cacheMap[headline] = data;
      renderBadge(badge, data);
      showTooltip(badge, data);
    } catch {
      badge.className = BADGE_CLASS + ' error';
      badge.innerHTML = '⚠ Offline';
      badge.title = 'FacTora server not running on localhost:5000';
    }
  });

  // Insert badge after the text node (doesn't break layout)
  el.appendChild(badge);
}

function renderBadge(badge, d) {
  const score = d.credibility_score || 0;
  const verdict = d.verdict || 'UNKNOWN';
  badge.className = BADGE_CLASS + ' ' + verdict.toLowerCase();
  const emoji = verdict === 'REAL' ? '✅' : '🚨';
  badge.innerHTML = `${emoji} ${score.toFixed(0)}% – ${verdict}`;
}

// ─── Tooltip ───────────────────────────────────────────────────────────────
function showTooltip(anchor, d) {
  removeTooltips();

  const rect = anchor.getBoundingClientRect();
  const score = d.credibility_score || 0;
  const color = d.color || '#374151';
  const factors = d.factors || {};

  const tip = document.createElement('div');
  tip.className = TOOLTIP_CLASS;
  tip.innerHTML = `
    <div class="factora-tooltip-header">
      <span class="factora-tooltip-logo">⚡ FacTora</span>
      <span style="flex:1"></span>
      <span style="font-size:.7rem;color:rgba(255,255,255,.35);">AI Fact Check</span>
    </div>
    <div class="factora-tooltip-score" style="color:${color}">${score.toFixed(0)}</div>
    <div class="factora-tooltip-grade-row">
      <span class="factora-grade" style="background:${color};color:#fff">${d.grade || '?'}</span>
      <span class="factora-label">${d.label || ''}</span>
    </div>
    ${factorBar('AI Model', factors.bert?.score ?? 0)}
    ${factorBar('Language', factors.linguistic?.score ?? 0)}
    ${factorBar('Source', factors.source?.score ?? 0)}
    ${factors.source?.badge ? `<div class="factora-source-badge">${factors.source.badge}</div>` : ''}
    <a class="factora-open-btn" href="http://localhost:5000" target="_blank">Open FacTora →</a>
  `;

  // Position it
  let top = rect.bottom + window.scrollY + 6;
  let left = rect.left + window.scrollX;
  if (left + 280 > window.innerWidth) left = window.innerWidth - 290;
  if (top + 260 > window.scrollY + window.innerHeight) top = rect.top + window.scrollY - 270;

  tip.style.top  = `${Math.max(8, top)}px`;
  tip.style.left = `${Math.max(8, left)}px`;
  tip.style.position = 'absolute';

  document.body.appendChild(tip);
  activeTooltip = tip;

  // Allow clicks on the open button
  setTimeout(() => { tip.style.pointerEvents = 'all'; }, 50);

  document.addEventListener('click', removeTooltips, { once: true });
}

function factorBar(name, score) {
  const color = score >= 70 ? '#22c55e' : score >= 45 ? '#eab308' : '#ef4444';
  return `
    <div class="factora-bar-row">
      <span class="factora-bar-name">${name}</span>
      <div class="factora-bar-wrap"><div class="factora-bar" style="width:${score}%;background:${color}"></div></div>
      <span class="factora-bar-val">${score.toFixed(0)}</span>
    </div>`;
}

function removeTooltips() {
  document.querySelectorAll('.' + TOOLTIP_CLASS).forEach(el => el.remove());
  activeTooltip = null;
}

// ─── Run ───────────────────────────────────────────────────────────────────
processHeadlines();

// Watch for dynamic content (SPAs, infinite scroll)
const observer = new MutationObserver(() => {
  clearTimeout(observer._t);
  observer._t = setTimeout(processHeadlines, 600);
});
observer.observe(document.body, { childList: true, subtree: true });
