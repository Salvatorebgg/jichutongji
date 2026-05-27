/* ── Data Preview Module ──────────────────────────────────── */

function renderDataPreview() {
  // Data preview is rendered inline via updatePreviewTable() in app.js
}

function updateAllSelectors() {
  setTimeout(() => {
    if (typeof buildVarControls === 'function') {
      buildVarControls();
    }
    if (typeof populateDescVarSelect === 'function') {
      populateDescVarSelect();
    }
  }, 100);
}
