import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const source = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
const manifest = JSON.parse(await readFile(new URL("../game-manifest.json", import.meta.url), "utf8"));

test("all six book codes are present and optional", () => {
  const codes = ["ROOMSTAR", "BOXCLUE", "QUIETWINGS", "BLANKEDGE", "CURTAINMAP", "TWODOORS"];
  for (const code of codes) assert.match(source, new RegExp(`code: \\"${code}\\"`));
  assert.equal(manifest.codes_required_for_progress, false);
  assert.equal(manifest.codes_hidden_in_book_scenes, true);
  assert.equal(manifest.scientific_content_locked_behind_codes, false);
  assert.match(source, /never block the story, explanation or next scene/i);
  assert.match(source, /word-definition/);
  assert.match(source, /no object has been shown for us to look at yet/i);
  assert.match(source, /hidden inside Book One’s reveal pictures/i);
  assert.doesNotMatch(source, /which happening|container and the looking|declared mark|no ring happened/i);
});

test("the book remains a distinct and valuable reading route", () => {
  for (const pageRange of ["pages 3–4", "pages 5–6", "pages 7–9", "pages 10–11", "pages 12–13", "pages 14–15", "pages 16–17", "pages 18–26"]) {
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

test("the narrative has a declared cause for all five stars and the final door", () => {
  assert.match(source, /five checked clues will light five stars/i);
  assert.match(source, /Practice complete:[\s\S]*No star lights/i);
  for (const star of [1, 2, 3, 4, 5]) assert.match(source, new RegExp(`star: ${star}`));
  assert.match(source, /With Clue Five checked, the fifth map star lights and the Star Door can open/i);
  assert.match(source, /All five stars shine\. The Star Door opens/i);
  assert.match(source, /later memory check/i);
  assert.match(source, /Memory spark earned/i);
});
