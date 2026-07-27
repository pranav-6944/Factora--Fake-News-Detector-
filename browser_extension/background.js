/**
 * FacTora Browser Extension – Background Service Worker
 * Handles extension lifecycle events and message passing.
 */

// On install: set default settings
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    factora_enabled:     true,
    auto_scan_headlines: true,
    factora_api_base:    'http://localhost:5000',
  });
  console.log('[FacTora] Extension installed. API: http://localhost:5000');
});

// Message relay from popup → content script (if needed)
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'PING') {
    sendResponse({ status: 'ok' });
  }
  return true;
});
