// Reference solution.
const TONES = new Set(["neutral", "info", "success", "warning", "danger"]);

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

export function renderBadge({ label, count = 0, tone = "neutral" } = {}) {
  const t = TONES.has(tone) ? tone : "neutral";
  const n = Number.isInteger(count) && count >= 0 ? count : 0;
  const display = n >= 100 ? "99+" : String(n);
  const text = esc(label && String(label).length ? label : "Badge");
  return `<span class="badge badge--${t}" role="status" aria-label="${text}: ${display}">${text}<b>${display}</b></span>`;
}
