import { createHash } from "node:crypto";

export function sha256(text) {
  return createHash("sha256").update(text, "utf8").digest("hex");
}
