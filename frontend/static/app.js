/**
 * app.js – gemeinsame Hilfsfunktionen für Switch GUI
 */

/**
 * Escaped einen String gegen XSS für die HTML-Ausgabe.
 * @param {string} str
 * @returns {string}
 */
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
