import { test } from "node:test";
import assert from "node:assert/strict";
import { renderBadge } from "../src/badge.js";

test("caps at 99+", () => {
  assert.equal(renderBadge({ label: "A", count: 100 }), '<span class="badge badge--neutral" role="status" aria-label="A: 99+">A<b>99+</b></span>');
  assert.match(renderBadge({ label: "A", count: 99 }), /<b>99<\/b>/);
});
test("negative and non-integer counts render 0", () => {
  assert.match(renderBadge({ label: "A", count: -3 }), /<b>0<\/b>/);
  assert.match(renderBadge({ label: "A", count: 2.5 }), /<b>0<\/b>/);
  assert.match(renderBadge({ label: "A", count: "7" }), /<b>0<\/b>/);
});
test("unknown tone falls back to neutral", () => {
  assert.match(renderBadge({ label: "A", tone: "purple" }), /badge--neutral/);
  assert.match(renderBadge({ label: "A", tone: "danger" }), /badge--danger/);
});
test("escapes label in text and aria-label", () => {
  const out = renderBadge({ label: '<b>&"x\'</b>', count: 1 });
  assert.ok(!out.includes("<b>&"));
  assert.ok(out.includes('aria-label="&lt;b&gt;&amp;&quot;x&#39;&lt;/b&gt;: 1"'));
  assert.ok(out.includes('&lt;b&gt;&amp;&quot;x&#39;&lt;/b&gt;<b>1</b>'));
});
test("missing label renders Badge", () => {
  assert.equal(renderBadge({}), '<span class="badge badge--neutral" role="status" aria-label="Badge: 0">Badge<b>0</b></span>');
  assert.match(renderBadge({ label: "" }), /Badge<b>0<\/b>/);
});
test("no trailing whitespace", () => {
  const out = renderBadge({ label: "A" });
  assert.equal(out, out.trim());
  assert.ok(!out.includes("\n"));
});
test("default count is 0", () => {
  assert.match(renderBadge({ label: "Z" }), /aria-label="Z: 0"/);
});
