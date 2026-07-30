import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const source = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
const manifest = JSON.parse(await readFile(new URL("../game-manifest.json", import.meta.url), "utf8"));

test("all six book codes are present and optional", () => {
  const codes = ["ROOMSTAR", "BOXCLUE", "QUIETWINGS", "BLANKEDGE", "CURTAINMAP", "TWODOORS"];
  for (const code of codes) assert.match(source, new RegExp(`code: \\"${code}\\"`));
  assert.equal(manifest.codes_required_for_progress, false);
  assert.equal(manifest.scientific_content_locked_behind_codes, false);
  assert.match(source, /never required to learn or continue/i);
  assert.match(source, /Word helper/);
  assert.match(source, /no object has been shown for us to look at yet/i);
});

test("the book remains the primary explanation", () => {
  for (const pageRange of ["pages 5-6", "pages 7-9", "pages 10-11", "pages 12-15", "pages 16-17", "pages 18-26"]) {
    assert.match(source, new RegExp(pageRange));
  }
  assert.equal(manifest.network_required_after_install, false);
  assert.equal(manifest.personal_data_collected, false);
  assert.equal(manifest.analytics_enabled, false);
  assert.equal(manifest.remote_hosting_ready, false);
});

test("the game contains no application network or analytics call", () => {
  assert.doesNotMatch(source, /\bfetch\s*\(/);
  assert.doesNotMatch(source, /XMLHttpRequest|WebSocket|navigator\.sendBeacon|gtag\s*\(/);
  assert.match(source, /localStorage\.removeItem/);
});
