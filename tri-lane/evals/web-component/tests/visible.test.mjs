import { test } from "node:test";
import assert from "node:assert/strict";
import { renderBadge } from "../src/badge.js";

test("basic render", () => {
  assert.equal(renderBadge({ label: "Unread", count: 12, tone: "info" }),
    '<span class="badge badge--info" role="status" aria-label="Unread: 12">Unread<b>12</b></span>');
});
