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
  assert.match(styles, /\.actor-mira img \{[^}]*bottom:-18px/);
  assert.match(styles, /\.actor-mira \{[^}]*height:auto;[^}]*aspect-ratio:2\/3/);
  assert.match(styles, /\.opening-cast \{[^}]*top:1%;[^}]*height:34%/);
  assert.doesNotMatch(source, /choice-grid|scene-choice|interaction-panel|window\.scrollTo/);
  for (const activity of ["note", "box", "bell", "card", "word", "curtain", "doors"]) assert.match(source, new RegExp(`scene.activity === \\"${activity}\\"`));
  assert.match(source, /className="emoji-prop recall-box/);
  assert.match(source, /Find the note among three objects/);
  assert.match(source, /Play again/);
  assert.equal(manifest.levels.length, 8);
  assert.equal(manifest.interaction_system.length, manifest.levels.length);
  assert.match(manifest.mini_game_policy, /Every stage in every level or book.*mini-game/i);
});

test("the landing page selects levels without browser-edge page movement", () => {
  assert.match(source, /className="level-grid"/);
  assert.match(source, /LEVEL 1 · READY/);
  assert.match(source, /LEVEL 2 · NEXT/);
  assert.match(source, /showLevelSelect/);
  assert.match(styles, /html,body \{[^}]*overflow:hidden;[^}]*overscroll-behavior:none/);
  assert.match(styles, /\.play-stage \{[^}]*overflow:hidden;[^}]*overscroll-behavior:none/);
  assert.equal(manifest.level_select.enabled, true);
  assert.match(manifest.mobile_navigation_guard, /prevent accidental pull-to-refresh/i);
});

test("automatic narration plays each story beat once and stops at the activity boundary", () => {
  assert.match(source, /lastAutoLineRef\.current === lineKey/);
  assert.match(source, /dialogueDone && !complete/);
  assert.match(source, /setTimeout\(\(\) => \{/);
});

test("the coherent child story has visible causes and short natural dialogue", () => {
  for (const phrase of [
    "Star Door woke with a clunk", "followed the first arrow across the observatory", "next glowing arrow into the bell room",
    "through the blue door to look for nothing in the paper room", "golden arrow led the four friends to a red curtain",
    "five bright stars opened the great Star Door", "carried the bright map into the library",
  ]) assert.match(source, new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  assert.doesNotMatch(source, /operational distinction|candidate grammar|presented record|declared check|occurrence/);
  assert.match(source, /The empty box is still here\. Empty means the toy is not inside/);
  assert.match(source, /Hidden is not gone/);
  assert.match(source, /B showed no object, so we do not invent one/);
  assert.doesNotMatch(source, /\bShh\b|Vee|Moss|Luma/);
});

test("Kokoro narration is caption matched, bundled and offline", async () => {
  assert.equal(narration.lines.length, 34);
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

test("every stage background and the permanent trio plus one E01 guest are declared", async () => {
  for (let index = 1; index <= 6; index += 1) {
    const name = String(index).padStart(2, "0");
    const match = source.match(new RegExp(`e01-stage-${name}-[^\"]+\\.png`));
    assert.ok(match, `stage ${name} is referenced`);
    await access(new URL(`../public/art/stages/${match[0]}`, import.meta.url));
  }
  assert.deepEqual(continuity.main_cast.map((character) => character.id), ["sol", "tavi", "mira"]);
  assert.equal(continuity.guest_characters.length, 1);
  assert.equal(continuity.guest_characters[0].id, "nori");
  assert.equal(continuity.guest_characters[0].introduced_in, "E01");
  assert.match(continuity.guest_characters[0].return_rule, /cannot identify the new answer/i);
  assert.match(continuity.policy, /no more than one new guest character/i);
});
