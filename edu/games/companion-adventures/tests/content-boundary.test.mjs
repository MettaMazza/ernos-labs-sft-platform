import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

const source = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
const levelTwo = await readFile(new URL("../app/level-two.tsx", import.meta.url), "utf8");
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
  assert.match(source, /Find the note among three things/);
  assert.match(source, /The note has landed next to Mira/);
  assert.match(source, /Mira is holding the note/);
  assert.match(styles, /@keyframes note-lands/);
  assert.match(styles, /@keyframes note-lifts/);
  assert.match(source, /Play again/);
  assert.equal(manifest.level_1.scenes.length, 8);
  assert.equal(manifest.interaction_system.level_1.length, manifest.level_1.scenes.length);
  assert.match(manifest.mini_game_policy, /Every stage in every level or book.*mini-game/i);
});

test("the landing page selects levels without browser-edge page movement", () => {
  assert.match(source, /className="level-grid"/);
  assert.match(source, /LEVEL 1 · READY/);
  assert.match(source, /LEVEL 2 · READY/);
  assert.match(source, /showLevelSelect/);
  assert.match(styles, /html,body \{[^}]*overflow:hidden;[^}]*overscroll-behavior:none/);
  assert.match(styles, /\.play-stage \{[^}]*overflow:hidden;[^}]*overscroll-behavior:none/);
  assert.equal(manifest.level_select.enabled, true);
  assert.match(manifest.mobile_navigation_guard, /prevent accidental pull-to-refresh/i);
});

test("completed levels always have a reachable mobile escape", () => {
  assert.match(styles, /\.ending-screen \{[^}]*height:100dvh;[^}]*overflow-y:auto;[^}]*overscroll-behavior:contain/);
  assert.match(styles, /\.ending-home \{[^}]*position:fixed;[^}]*z-index:40/);
  assert.match(source, /className="ending-home" onClick=\{showLevelSelect\}/);
  assert.match(levelTwo, /className="ending-home" onClick=\{onExit\}/);
  assert.match(levelTwo, /progress\.finished === true \? "select" : "e02"/);
  assert.match(source, /savedLevelTwoRooms === 9 \? "Play Level 2 again"/);
});

test("automatic narration plays each story beat once and stops at the activity boundary", () => {
  assert.match(source, /lastAutoLineRef\.current === lineKey/);
  assert.match(source, /dialogueDone && !complete/);
  assert.match(source, /setTimeout\(\(\) => \{/);
});

test("the coherent child story has visible causes and short natural dialogue", () => {
  for (const phrase of [
    "The Star Door was shut", "A note came through the letter box",
    "Mira picked up the note and opened it", "My brown teddy is inside",
    "Tap the toy to lift it out. Then tap the box", "The first star turned gold. A blue door opened",
    "The friends went through the door", "I found a white card on this table",
    "seven wall tiles lit up, one after another", "My teddy rolled out of my bag",
    "Now all five stars were gold, and the Star Door opened", "Mira folded the note",
  ]) assert.match(source, new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  assert.doesNotMatch(source, /operational distinction|candidate grammar|presented record|declared check|occurrence|registered partition|generated item|fitted tray/);
  assert.match(source, /Empty means there is no toy inside this box\. The box is still here/);
  assert.match(source, /Hidden means it was there, but the curtain stopped us from seeing it/);
  assert.match(source, /Door B showed an empty shelf/);
  assert.doesNotMatch(source, /woke with a clunk|brass|rectangular slot|folded paper note|Now the box has nothing in it|My toy! I knew I packed you/);
  assert.doesNotMatch(source, /\bShh\b|Vee|Moss|Luma/);
});

test("mobile page restoration returns to the exact active turn instead of the title", () => {
  for (const field of ["started", "finished", "sceneIndex", "beat", "activityStep", "complete", "letters", "curtain", "doors", "drawn", "cardOpen"]) {
    assert.match(source, new RegExp(`\\b${field}\\b`));
  }
  assert.match(source, /typeof saved\.started === "boolean"\) setStarted\(saved\.started\)/);
  assert.match(source, /localStorage\.setItem\("sft-e01-moving-stage-v1"/);
  assert.match(source, /storageReadyRef\.current/);
  assert.match(source, /!storageReady && <div className="restore-screen"/);
  assert.match(source, /window\.addEventListener\("pagehide", saveNow\)/);
  assert.match(source, /document\.addEventListener\("visibilitychange", saveWhenHidden\)/);
});

test("Kokoro narration is caption matched, bundled and offline", async () => {
  assert.equal(narration.lines.length, 35);
  assert.equal(manifest.network_required_after_install, false);
  assert.match(manifest.sound_system, /Kokoro narration lines plus offline Web Audio/i);
  for (const [filename, speaker, caption] of narration.lines) {
    assert.match(source, new RegExp(`audio: \\"${filename}\\"`));
    assert.ok(source.includes(`speaker: "${speaker}", text: "${caption.replaceAll('"', '\\"')}"`));
    await access(new URL(`../public/audio/e01-v1.6.0/${filename}.mp3`, import.meta.url));
  }
  await access(new URL("../public/audio/e01-v1.6.0/generation-receipt.json", import.meta.url));
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
  assert.equal(continuity.guest_characters.length, 2);
  assert.equal(continuity.guest_characters[0].id, "nori");
  assert.equal(continuity.guest_characters[0].introduced_in, "E01");
  assert.match(continuity.guest_characters[0].return_rule, /cannot identify the new answer/i);
  assert.equal(continuity.guest_characters[1].id, "pax");
  assert.equal(continuity.guest_characters[1].introduced_in, "E02");
  assert.match(continuity.policy, /no more than one new guest character/i);
});

test("Level Two has nine distinct multi-step replayable mini-games and one new guest", async () => {
  for (const activity of ["parcel", "whole", "bridge", "parts", "rebuild", "match", "gap", "count", "recall"]) {
    assert.match(levelTwo, new RegExp('scene.activity === "' + activity + '"'));
  }
  for (const title of ["Parcel Dash", "Lantern Detective", "Fit-the-Circle Lab", "Twin-Part Test", "Doorway Delivery", "Count-and-Collect", "Gap Repair", "Lantern Builder", "Memory Moonwalk"]) {
    assert.match(levelTwo, new RegExp('gameTitle: "' + title + '"'));
    assert.ok(manifest.interaction_system.level_2.some((description) => description.startsWith(title + ":")));
  }
  assert.equal((levelTwo.match(/gameTitle: "/g) ?? []).length, 9);
  for (const mechanic of ["Undo every ribbon", "Inspect the whole", "Fit part", "Measure both equal parts", "Pick one lantern part first", "collected", "Repair spark", "Wake light", "Cross in order"]) {
    assert.ok(levelTwo.includes(mechanic), mechanic + " is implemented");
  }
  assert.match(levelTwo, /MINI-GAME/);
  assert.equal((levelTwo.match(/id: "/g) ?? []).length, 9);
  assert.match(levelTwo, /New friend for Level Two/);
  assert.match(levelTwo, /introduces: "pax"/);
  assert.doesNotMatch(levelTwo, /introduces: "(?:mira|tavi|sol|nori)"/);
  assert.match(levelTwo, /Play again/);
  assert.match(levelTwo, /Follow the plan/);
  assert.equal(manifest.level_2.scenes.length, 9);
  assert.equal(manifest.interaction_system.level_2.length, manifest.level_2.scenes.length);
  for (let index = 2; index <= 8; index += 1) {
    const name = String(index).padStart(2, "0");
    const match = levelTwo.match(new RegExp('e02-stage-' + name + '-[^"]+\\.png'));
    assert.ok(match, "E02 stage " + name + " is referenced");
    await access(new URL("../public/art/stages/" + match[0], import.meta.url));
  }
});

test("Level Two language is simple, causal and does not give answers before play", () => {
  for (const phrase of [
    "parcel from the last adventure rolled down the library ramp",
    "Let’s open it and see what is inside",
    "The lantern was too wide to fit through it",
    "Mission: get the whole lantern through the small door",
    "take the lantern apart, carry every part through, and build the whole lantern again",
    "All four lantern parts made it through. None was left behind",
    "The same whole lantern is back",
    "The plan worked",
  ]) assert.ok(levelTwo.includes(phrase));
  assert.doesNotMatch(levelTwo, /next door|next room|first door opens|last door opens/i);
  assert.doesNotMatch(levelTwo, /great brass|brass rectangular|magical door|registered|partition|fitted tray|coordinate|gold seal|door woke/i);
});

test("Level Two Kokoro narration matches every visible caption and is bundled", async () => {
  const levelTwoNarration = JSON.parse(await readFile(new URL("../narration-manifest-e02.json", import.meta.url), "utf8"));
  assert.equal(levelTwoNarration.lines.length, 27);
  for (const [filename, speaker, caption] of levelTwoNarration.lines) {
    assert.match(levelTwo, new RegExp('audio: "' + filename + '"'));
    assert.ok(levelTwo.includes('speaker: "' + speaker + '", text: "' + caption.replaceAll('"', '\\"') + '"'));
    await access(new URL("../public/audio/e02-v1.0.0/" + filename + ".mp3", import.meta.url));
  }
  await access(new URL("../public/audio/e02-v1.0.0/generation-receipt.json", import.meta.url));
  assert.doesNotMatch(levelTwo, /\bfetch\s*\(|XMLHttpRequest|WebSocket|sendBeacon/);
});

test("both levels restore locally and tab switching does not reset the story", () => {
  assert.match(source, /sft-active-level-v1/);
  assert.match(levelTwo, /sft-e02-moving-stage-v1/);
  assert.match(levelTwo, /window\.addEventListener\("pagehide", save\)/);
  assert.match(levelTwo, /document\.addEventListener\("visibilitychange", hidden\)/);
  for (const field of ["sceneIndex", "beat", "complete", "finished", "activityStep", "chosen"]) {
    assert.match(levelTwo, new RegExp("\\b" + field + "\\b"));
  }
});
