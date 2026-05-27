/* ── Three-Line Table Generator ───────────────────────────── */

function initTableGenerator() {
  // Table generation is triggered via the descriptive tab and analysis results
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}
