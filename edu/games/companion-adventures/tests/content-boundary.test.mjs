import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

const source = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
const styles = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
const manifest = JSON.parse(await readFile(new URL("../game-manifest.json", import.meta.url), "utf8"));
const narration = JSON.parse(await readFile(new URL("../narration-manifest.json", import.meta.url), "utf8"));
const continuity = JSON.parse(await readFile(new URL("../character-continuity.json", import.meta.url), "utf8"));

test("Level One is a fixed animated stage, not a read-and-scroll choice menu", () => {
  assert.match(styles, /height:100dvh;[^}]*overflow:hidden/);
  assert.match(styles, /@keyframes actor-walks-in/);
  assert.match(styles, /@keyframes actor-idles/);
  assert.match(styles, /@keyframes actor-speaks/);
  assert.doesNotMatch(source, /choice-grid|scene-choice|interaction-panel|window\.scrollTo/);
  for (const activity of ["box", "bell", "card", "word", "curtain", "doors"]) assert.match(source, new RegExp(`scene.activity === \\"${activity}\\"`));
  assert.match(source, /className="stage-prop recall-box/);
});

test("the coherent child story has visible causes and short natural dialogue", () => {
  for (const phrase of [
    "Star Door woke with a clunk", "The first clue was tucked inside the parcel", "The wind has stopped",
    "The card made the wall tiles glow", "I can make Sol's toy vanish", "Five clues. Five stars",
    "The crew carried the bright map into the library",
  ]) assert.match(source, new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  assert.doesNotMatch(source, /operational distinction|candidate grammar|presented record|declared check|occurrence/);
  assert.match(source, /The empty box is still here\. Empty means the toy is not inside/);
  assert.match(source, /Hidden is not gone/);
  assert.match(source, /B showed no object, so we do not invent one/);
});

test("Kokoro narration is caption matched, bundled and offline", async () => {
  assert.equal(narration.lines.length, 28);
  assert.equal(manifest.network_required_after_install, false);
  assert.match(manifest.sound_system, /Kokoro narration.*offline Web Audio/i);
  for (const [filename, speaker, caption] of narration.lines) {
    assert.match(source, new RegExp(`audio: \\"${filename}\\"`));
    assert.ok(source.includes(`speaker: "${speaker}", text: "${caption.replaceAll('"', '\\"')}"`));
    await access(new URL(`../public/audio/e01/${filename}.mp3`, import.meta.url));
  }
  await access(new URL("../public/audio/e01/generation-receipt.json", import.meta.url));
  assert.doesNotMatch(source, /\bfetch\s*\(|XMLHttpRequest|WebSocket|sendBeacon/);
});

test("book codes are optional and callbacks never reveal new answers", () => {
  for (const code of ["ROOMSTAR", "BOXCLUE", "QUIETWINGS", "BLANKEDGE", "CURTAINMAP", "TWODOORS"]) assert.match(source, new RegExp(code));
  assert.equal(manifest.codes_required_for_progress, false);
  assert.equal(manifest.scientific_content_locked_behind_codes, false);
  assert.match(continuity.policy, /must never state or expose the new answer/i);
  assert.ok(continuity.callback_guardrails.every((rule) => !/give the answer/i.test(rule)));
  assert.match(source, /never lessons or progress/i);
});

test("every stage background and the recurring Tavi record are declared", async () => {
  for (let index = 1; index <= 6; index += 1) {
    const name = String(index).padStart(2, "0");
    const match = source.match(new RegExp(`e01-stage-${name}-[^\"]+\\.png`));
    assert.ok(match, `stage ${name} is referenced`);
    await access(new URL(`../public/art/stages/${match[0]}`, import.meta.url));
  }
  assert.equal(continuity.characters[0].id, "tavi");
  assert.equal(continuity.characters[0].introduced_in, "E01");
  assert.match(continuity.characters[0].return_rule, /cannot identify the new answer/i);
});
