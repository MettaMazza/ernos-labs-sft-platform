import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { access, readFile } from "node:fs/promises";
import test from "node:test";
import { levelThreeRelayForRound, pendingLevelThreeResolution, readLevelThreeIntroSeen, readLevelThreeResolution } from "../app/level-three-state.mjs";

const source = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
const levelTwo = await readFile(new URL("../app/level-two.tsx", import.meta.url), "utf8");
const levelThree = await readFile(new URL("../app/level-three.tsx", import.meta.url), "utf8");
const levelPrelude = await readFile(new URL("../app/level-prelude.tsx", import.meta.url), "utf8");
const levelMusic = await readFile(new URL("../app/use-level-music.ts", import.meta.url), "utf8");
const styles = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
const gameplayStandard = await readFile(new URL("../GAMEPLAY_STANDARD.md", import.meta.url), "utf8");
const manifest = JSON.parse(await readFile(new URL("../game-manifest.json", import.meta.url), "utf8"));
const claimMap = JSON.parse(await readFile(new URL("../claim-map.json", import.meta.url), "utf8"));
const narration = JSON.parse(await readFile(new URL("../narration-manifest.json", import.meta.url), "utf8"));
const levelTwoNarration = JSON.parse(await readFile(new URL("../narration-manifest-e02.json", import.meta.url), "utf8"));
const levelThreeNarration = JSON.parse(await readFile(new URL("../narration-manifest-e03.json", import.meta.url), "utf8"));
const continuity = JSON.parse(await readFile(new URL("../character-continuity.json", import.meta.url), "utf8"));
const e02Book = JSON.parse(await readFile(new URL("../../../books/E02-one-whole-many-parts/source/book-v1.0.0.json", import.meta.url), "utf8"));
const e03Book = JSON.parse(await readFile(new URL("../../../books/E03-the-fold-makes-a-pattern/source/book-v1.0.0.json", import.meta.url), "utf8"));
const e03ClaimMap = JSON.parse(await readFile(new URL("../../../books/E03-the-fold-makes-a-pattern/claim-map.json", import.meta.url), "utf8"));
const e03AdultGuide = await readFile(new URL("../../../books/E03-the-fold-makes-a-pattern/adult-guide.md", import.meta.url), "utf8");

function assertCaptionLine(component, [filename, speaker, caption]) {
  const audioMarker = `audio: "${filename}"`;
  const audioIndex = component.indexOf(audioMarker);
  assert.notEqual(audioIndex, -1, `${filename} is referenced`);
  const objectStart = component.lastIndexOf("{", audioIndex);
  const objectEnd = component.indexOf("}", audioIndex);
  const lineObject = component.slice(objectStart, objectEnd + 1);
  assert.ok(lineObject.includes(`speaker: "${speaker}"`), `${filename} keeps its speaker`);
  const expectedCaption = `text: "${caption.replaceAll('"', '\\"')}"`.toLocaleLowerCase();
  assert.ok(lineObject.toLocaleLowerCase().includes(expectedCaption), `${filename} keeps its caption text`);
}

test("Level One is a fixed animated stage, not a read-and-scroll choice menu", () => {
  assert.match(styles, /height:100dvh;[^}]*overflow:hidden/);
  assert.match(styles, /@keyframes actor-walks-in/);
  assert.match(styles, /@keyframes actor-idles/);
  assert.match(styles, /@keyframes actor-speaks/);
  assert.match(styles, /\.actor-mira img \{[^}]*bottom:-18px/);
  assert.match(styles, /\.actor-mira \{[^}]*height:auto;[^}]*aspect-ratio:2\/3/);
  assert.match(styles, /\.opening-cast \{[^}]*top:1%;[^}]*height:min\(30vh,260px\)/);
  assert.match(styles, /\.activity-layer \{[^}]*inset:68px 54px 162px 0/);
  assert.doesNotMatch(source, /choice-grid|scene-choice|interaction-panel|window\.scrollTo/);
  for (const activity of ["note", "box", "bell", "card", "word", "curtain", "doors"]) assert.match(source, new RegExp(`scene.activity === \\"${activity}\\"`));
  assert.match(source, /const recallChoices = \{/);
  assert.match(source, /recall-\$\{kind\}/);
  assert.match(source, /Find the note among three things/);
  assert.match(source, /The note has landed next to Mia/);
  assert.match(source, /Mia is holding the note/);
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
  assert.match(levelTwo, /className="ending-home" onClick=\{exitLevel\}/);
  assert.match(levelThree, /className="ending-home" onClick=\{exitLevel\}/);
  for (const component of [levelTwo, levelThree]) {
    assert.match(component, /function exitLevel\(\) \{[^}]*stopMusic\(\); onExit\(\); \}/);
  }
  assert.match(levelTwo, /function goToNextLevel\(\) \{[^}]*stopMusic\(\); onNext\(\); \}/);
  assert.match(levelTwo, /localStorage\.setItem\("sft-active-level-v1", "e02"\)/);
  assert.match(levelThree, /localStorage\.setItem\("sft-active-level-v1", "e03"\)/);
  assert.match(source, /savedLevelTwoRooms === 9 \? "Review Level 2 ending"/);
  assert.match(source, /savedLevelThreeStages === 9 \? "Review Level 3 ending"/);
});

test("automatic narration plays each story beat once and stops at the activity boundary", () => {
  assert.match(source, /lastAutoLineRef\.current === lineKey/);
  assert.match(source, /dialogueDone && !complete/);
  assert.match(source, /setTimeout\(\(\) => \{/);
});

test("the coherent child story has visible causes and short natural dialogue", () => {
  for (const phrase of [
    "the Star Door was closed", "A note slid through the letter box",
    "Mia saw the note, picked it up and opened it", "My brown teddy is inside",
    "Tap the toy to lift it out. Then tap the box", "The first star turned gold. A blue door opened",
    "The friends went through the door", "I found a white card on this table",
    "seven wall tiles lit up, one after another", "My teddy rolled out of my bag",
    "Now all five stars were gold, and the Star Door opened", "Mia folded the note",
  ]) assert.match(source, new RegExp(phrase.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  assert.doesNotMatch(source, /operational distinction|candidate grammar|presented record|declared check|occurrence|registered partition|generated item|fitted tray/);
  assert.match(source, /Empty means the teddy is not inside the box now\. The box is still here/);
  assert.match(source, /It was hidden: the curtain stopped you from seeing it, but the teddy stayed behind the curtain/);
  assert.match(source, /The other held an empty shelf/);
  assert.match(source, /B showed no object/);
  assert.doesNotMatch(source, /woke with a clunk|brass|rectangular slot|folded paper note|Now the box has nothing in it|My toy! I knew I packed you/);
  assert.doesNotMatch(source, /\bShh\b|Vee|Moss|Luma/);
});

test("mobile page restoration returns to the exact active turn instead of the title", () => {
  for (const field of ["started", "finished", "sceneIndex", "beat", "activityStep", "complete", "letters", "curtain", "doors", "drawn", "cardOpen"]) {
    assert.match(source, new RegExp(`\\b${field}\\b`));
  }
  assert.match(source, /restoreLevelOneProgress\(localStorage\.getItem\(LEVEL_ONE_STORAGE_KEY\)/);
  assert.match(source, /localStorage\.setItem\(LEVEL_ONE_STORAGE_KEY/);
  assert.match(source, /setPreludeStep\(saved\.preludeStep\)/);
  assert.match(source, /setResolution\(saved\.resolution\)/);
  assert.match(source, /if \(!storageReady\) return;/);
  assert.match(source, /!storageReady && <div className="restore-screen"/);
  assert.match(source, /window\.addEventListener\("pagehide", saveNow\)/);
  assert.match(source, /document\.addEventListener\("visibilitychange", saveWhenHidden\)/);
});

test("Kokoro narration is caption matched, bundled and offline", async () => {
  assert.equal(narration.lines.length, 40);
  assert.equal(levelTwoNarration.lines.length, 32);
  assert.equal(levelThreeNarration.lines.length, 32);
  assert.equal(narration.lines.length + levelTwoNarration.lines.length + levelThreeNarration.lines.length, 104);
  assert.equal(manifest.level_1.narrated_lines, 40);
  assert.equal(manifest.level_2.narrated_lines, 32);
  assert.equal(manifest.level_3.narrated_lines, 32);
  assert.equal(manifest.network_required_after_install, false);
  assert.match(manifest.sound_system, /104 caption-matched local Kokoro narration lines/i);
  assert.match(manifest.sound_system, /three distinct original offline background music tracks/i);
  assert.match(manifest.sound_system, /offline Web Audio movement and interaction effects/i);
  for (const line of narration.lines) {
    const [filename] = line;
    assertCaptionLine(source, line);
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
  assert.deepEqual(continuity.main_cast.map((character) => character.id), ["sol", "tavi", "mia"]);
  assert.equal(continuity.guest_characters.length, 3);
  assert.equal(continuity.guest_characters[0].id, "nori");
  assert.equal(continuity.guest_characters[0].introduced_in, "E01");
  assert.match(continuity.guest_characters[0].return_rule, /cannot identify the new answer/i);
  assert.equal(continuity.guest_characters[1].id, "pax");
  assert.equal(continuity.guest_characters[1].introduced_in, "E02");
  assert.equal(continuity.guest_characters[2].id, "vee");
  assert.equal(continuity.guest_characters[2].introduced_in, "E03");
  assert.match(continuity.policy, /no more than one new guest character/i);
});

test("Level Two has nine distinct multi-step replayable mini-games and one new guest", async () => {
  for (const activity of ["parcel", "whole", "bridge", "parts", "rebuild", "match", "gap", "count", "sum"]) {
    assert.match(levelTwo, new RegExp('scene.activity === "' + activity + '"'));
  }
  for (const title of ["Parcel Dash", "Lantern Detective", "Fit-the-Circle Lab", "Twin-Part Test", "Doorway Delivery", "Count-and-Collect", "Gap Repair", "Lantern Builder", "Lantern Sum Builder"]) {
    assert.match(levelTwo, new RegExp('gameTitle: "' + title + '"'));
    assert.ok(manifest.interaction_system.level_2.some((description) => description.startsWith(title + ":")));
  }
  assert.equal((levelTwo.match(/gameTitle: "/g) ?? []).length, 9);
  for (const mechanic of ["parcel-path-game", "whole-lantern-reveal", "plan-workbench", "balance-puzzle", "doorway-delivery", "lantern-count-game", "gap-fit-puzzle", "lantern-jigsaw", "lantern-sum-game"]) {
    assert.ok(levelTwo.includes(mechanic), mechanic + " is implemented");
  }
  assert.match(levelTwo, /MINI-GAME/);
  assert.equal((levelTwo.match(/^\s+id: "[a-z]+", title:/gm) ?? []).length, 9);
  assert.match(levelTwo, /New friend for Level Two/);
  assert.match(levelTwo, /introduces: "pax"/);
  assert.doesNotMatch(levelTwo, /introduces: "(?:mira|tavi|sol|nori)"/);
  assert.match(levelTwo, /Play again/);
  assert.match(levelTwo, /Follow the plan/);
  for (const contract of ["mistakes", "roundLost", "retryRound", "TryLights"]) assert.match(levelTwo, new RegExp(contract));
  assert.equal(manifest.level_2.scenes.length, 9);
  assert.equal(manifest.interaction_system.level_2.length, manifest.level_2.scenes.length);
  assert.deepEqual(manifest.level_2.scenes.slice(-2), ["sum", "rebuild"]);
  assert.match(levelTwo, /One part plus one part plus one part plus one part equals four parts/);
  assert.match(levelTwo, /4 PARTS → 1 WHOLE LANTERN/);
  assert.match(levelTwo, /The equation checked all four parts/);
  assert.match(levelTwo, /finished plan has matching sides; that is called symmetrical/i);
  assert.match(levelTwo, /This check teaches us to compare sizes instead of guessing from a quick look/);
  assert.match(levelTwo, /1: "top left", 2: "top right", 3: "bottom left", 4: "bottom right"/);
  assert.match(levelTwo, /Take all 4 parts to the round frame/);
  assert.doesNotMatch(levelTwo, /setActivityStep\(7\)/);
  assert.match(styles, /\.lantern-plan-frame \{ grid-template-columns:repeat\(2,clamp\(56px,12vw,72px\)\)/);
  assert.ok(manifest.level_2.scientific_sources.some((source) => source.claim_id === "SFT-MATH-EXACT-ARITHMETIC-001"));
  assert.ok(manifest.level_2.scientific_sources.some((source) => source.claim_id === "SFT-MATH-ARITH-JUNCTION-ADDITION-002"));
  for (const index of [2, 3, 4, 6, 7, 8]) {
    const name = String(index).padStart(2, "0");
    const match = levelTwo.match(new RegExp('e02-stage-' + name + '-[^"]+\\.png'));
    assert.ok(match, "E02 stage " + name + " is referenced");
    await access(new URL("../public/art/stages/" + match[0], import.meta.url));
  }
});

test("Level Two language is simple, causal and does not give answers before play", () => {
  for (const phrase of [
    "The parcel that slid down the library ramp after the first mystery",
    "The label says Mia, Sol and Tavi. It is for us!",
    "The lantern was too wide to fit through it",
    "Mission: get the whole lantern through the small door",
    "take the lantern apart, carry every part through, and build the whole lantern again",
    "You carried all four lantern parts through the small door. Each part moved once",
    "The same four parts became one whole again",
    "All four lantern parts were still separate",
  ]) assert.ok(levelTwo.includes(phrase));
  assert.doesNotMatch(levelTwo, /next door|next room|first door opens|last door opens/i);
  assert.doesNotMatch(levelTwo, /great brass|brass rectangular|magical door|registered|partition|fitted tray|coordinate|gold seal|door woke/i);
});

test("Book Two delays answers, keeps every part visible and reserves the final rebuild", () => {
  const page = (number) => e02Book.pages.find((entry) => entry.page === number);
  assert.match(page(16).subtext, /name for this matching shape comes after your choice/);
  assert.doesNotMatch(`${page(16).text} ${page(16).subtext}`, /symmetrical/i);
  assert.match(page(17).text, /Matching sides around the middle make a symmetrical plan/);
  assert.match(page(23).text, /three lantern parts into the round frame.*fourth part stayed on the tray/s);
  assert.doesNotMatch(page(23).text, /NOT YET|all four spaces were filled/);
  assert.match(page(24).text, /NOT YET\. ONE SPACE IS EMPTY/);
  assert.match(page(24).subtext, /returned all four parts to the tray for the real rebuild/);
  assert.match(page(25).text, /triangle belongs to the workshop, not the lantern/);
  assert.match(page(26).text, /Pax lifted two lantern parts\. Two more stayed on the tray/);
  assert.match(page(28).text, /1 PART \+ 1 PART \+ 1 PART \+ 1 PART = \?/);
  assert.match(page(29).text, /equals sign says the count on each side is the same: four parts/i);
  assert.doesNotMatch(e02Book.pages.filter((entry) => entry.page < 30).map((entry) => entry.text).join(" "), /same Moon Lantern was ONE WHOLE again/);
  assert.match(page(30).text, /four separate parts fitted together\. The Moon Lantern was one whole again/);
  assert.match(page(30).subtext, /arrow shows what happened next.*It is not an equals sign/);
});

test("Levels Two and Three use distinct consequence-bearing puzzle systems", () => {
  assert.match(gameplayStandard, /Three wrong moves end the round/i);
  for (const mechanic of ["light-catch-board", "two-side-lab", "gate-crank", "return-lane-puzzle", "pattern-conveyor", "rule-repair-board", "bridge-runner", "route-compare", "role-relay"]) {
    assert.ok(levelThree.includes(mechanic), mechanic + " is implemented");
    assert.match(styles, new RegExp("\\." + mechanic));
  }
  for (const contract of ["mistakes", "roundLost", "retryRound", "TryLights"]) assert.match(levelThree, new RegExp(contract));
  assert.match(levelTwo, /That round used all three try lights/);
  assert.match(levelThree, /Round over/);
  assert.match(source, /LEVEL 3 · READY/);
  assert.match(levelTwo, /Next level/);
  assert.match(levelThree, /Next level · coming soon/);
  assert.equal(manifest.level_3.scenes.length, 9);
  assert.equal(manifest.interaction_system.level_3.length, 9);
  assert.deepEqual(manifest.level_3.scientific_sources.map((source) => source.claim_id), ["SFT-FOUNDATION-FOLD-001", "SFT-FOUNDATION-FOLD-DYNAMICS-001"]);
  assert.deepEqual(claimMap.levels.E03.claim_ids, ["SFT-FOUNDATION-FOLD-001", "SFT-FOUNDATION-FOLD-DYNAMICS-001"]);
  assert.deepEqual(Object.keys(claimMap.levels.E03.scene_to_book_pages), manifest.level_3.scenes);
  assert.deepEqual([...new Set(Object.values(claimMap.levels.E03.scene_to_book_pages).flat())].sort((a,b)=>a-b), Array.from({length:30},(_,index)=>index+3));
  assert.deepEqual(manifest.level_3.reading_codes, e03Book.reading_codes.map((entry) => entry.code));
  assert.deepEqual(manifest.level_3.scientific_sources.map((entry) => entry.claim_id), e03ClaimMap.scientific_claims.map((entry) => entry.claim_id));
  assert.equal(claimMap.book_remains_distinct_deeper_reading_route, true);
  assert.doesNotMatch(JSON.stringify(manifest.level_3), /pending-review/i);
  assert.match(levelThree, /const lane = \(chosen\.length \+ mistakes \+ round\) % 3/);
  assert.doesNotMatch(levelThree, /setInterval|belt\[tick/);
  assert.match(levelThree, /className="conveyor-choices"/);
  assert.match(manifest.interaction_system.level_3.join(" "), /one-turn.*letter changes on replay/i);
  assert.match(levelThree, /aria-label="Restart Level Three"/);
  assert.match(levelThree, /onKeyDown=\{\(event\)=>\{if\(event\.key===\"Enter\"\|\|event\.key===\" \"\)\{event\.preventDefault\(\);flip\(\);\}\}\}/);
  assert.match(levelThree, /codeTreats/);
  assert.match(levelThree, /className="code-treat"/);
  assert.match(styles, /\.repair-row\{[^}]*grid-template-columns:repeat\(3,1fr\)/);
  assert.match(styles, /\.bridge-lanes\{[^}]*height:260px/);
  assert.match(styles, /\.route-map-cards\{[^}]*grid-template-columns:1fr/);
});

test("Level Three resumes past its prelude at the exact saved flow", () => {
  assert.equal(readLevelThreeIntroSeen({}, false), false);
  assert.equal(readLevelThreeIntroSeen({ introSeen: false, sceneIndex: 4 }, true), false);
  assert.equal(readLevelThreeIntroSeen({ introSeen: true }, true), true);
  assert.equal(readLevelThreeIntroSeen({ sceneIndex: 3 }, true), true);
  assert.equal(readLevelThreeIntroSeen({ sceneIndex: 0, beat: 1 }, true), true);
  assert.equal(readLevelThreeIntroSeen({ finished: true }, true), true);
  assert.match(levelThree, /const \[introSeen, setIntroSeen\] = useState\(false\)/);
  assert.match(levelThree, /const introOpen = !introSeen/);
  assert.match(levelThree, /progressRef\.current = \{ introSeen, sceneIndex, beat, complete, finished, activityStep, chosen, wrong, mistakes, roundLost, round, resolution \}/);
  assert.match(levelThree, /setIntroSeen\(readLevelThreeIntroSeen\(saved, stored !== null\)\)/);
  assert.match(levelThree, /setIntroSeen\(true\); lastLineRef\.current = ""/);
  assert.match(levelThree, /setIntroSeen\(false\); setResolution\(null\)/);
  assert.match(levelThree, /\[storageReady, introSeen, sceneIndex, beat, complete, finished, activityStep, chosen, wrong, mistakes, roundLost, round, resolution\]/);
});

test("Level Three success transitions survive reload and lock completed boards", () => {
  const terminalBoards = [
    ["trail", [1, 2, 1, 2], 0, "finish"],
    ["sides", [1, 2], 8, "finish"],
    ["continue", [1, 2, 1], 0, "finish"],
    ["bridge", [0, 1, 2, 3, 4], 1, "finish"],
    ["routes", [2, 3], 0, "finish"],
    ["transfer", [2, 1, 2], 0, "transfer-memory"],
  ];
  for (const [activity, chosen, step, expected] of terminalBoards) {
    assert.equal(pendingLevelThreeResolution(activity, chosen, step), expected);
  }
  assert.equal(pendingLevelThreeResolution("trail", [1, 2, 1], 0), null);
  assert.equal(pendingLevelThreeResolution("routes", [1, 2], 0), null);
  assert.equal(pendingLevelThreeResolution("transfer", [2, 1, 2], 1), null);
  assert.equal(readLevelThreeResolution("finish"), "finish");
  assert.equal(readLevelThreeResolution("transfer-memory"), "transfer-memory");
  assert.equal(readLevelThreeResolution("unknown"), null);

  assert.equal((levelThree.match(/beginResolution\("finish"\)/g) ?? []).length, 6);
  assert.equal((levelThree.match(/beginResolution\("transfer-memory"\)/g) ?? []).length, 1);
  assert.doesNotMatch(levelThree, /window\.setTimeout\(finish/);
  assert.match(levelThree, /setResolution\(readLevelThreeResolution\(saved\.resolution\)\)/);
  assert.match(levelThree, /const pendingResolution = resolution \?\? inferredResolution/);
  assert.match(levelThree, /return \(\) => window\.clearTimeout\(timeout\)/);
  assert.match(levelThree, /fieldset className="resolution-lock" disabled=\{resolving\} aria-busy=\{resolving\}/);
  assert.match(styles, /\.resolution-lock \{[^}]*display:contents/);
  assert.match(levelThree, /if \(roundLost \|\| resolving\) return/);
});

test("New-Role Relay changes its starting role on replay and stays deterministic", () => {
  assert.deepEqual(levelThreeRelayForRound(0), { start: "star", sequence: ["leaf", "star", "leaf"] });
  assert.deepEqual(levelThreeRelayForRound(1), { start: "leaf", sequence: ["star", "leaf", "star"] });
  assert.deepEqual(levelThreeRelayForRound(2), levelThreeRelayForRound(0));
  for (let round = 0; round < 8; round += 1) {
    const relay = levelThreeRelayForRound(round);
    const row = [relay.start, ...relay.sequence];
    assert.equal(row.length, 4);
    assert.ok(row.every((role, index) => index === 0 || role !== row[index - 1]));
  }
  assert.match(levelThree, /const relay = levelThreeRelayForRound\(round\)/);
  assert.match(levelThree, /icons\[relay\.start\]/);
  assert.match(levelThree, /first window already has a \$\{relay\.start\}/i);
});

test("Level Three bridge and relay narration match every visible step", async () => {
  const bridgeLine = levelThreeNarration.lines.find(([filename]) => filename === "21-mira-bridge-crossed");
  const relayLine = levelThreeNarration.lines.find(([filename]) => filename === "25-narrator-star-leaf");
  assert.ok(bridgeLine, "the bridge success narration is declared");
  assert.ok(relayLine, "the relay introduction narration is declared");

  const bridgeCaption = bridgeLine[2];
  assert.match(bridgeCaption, /across all five arches/i);
  assert.match(bridgeCaption, /over, under, over, under, over when the first sign said over/i);
  assert.match(bridgeCaption, /under, over, under, over, under when the first sign said under/i);
  assert.match(bridgeCaption, /alternated from one arch to the next/i);
  assert.doesNotMatch(bridgeCaption, /over, under, over, under across the bridge/i);

  const relayCaption = relayLine[2];
  assert.match(relayCaption, /Four windows opened/i);
  assert.match(relayCaption, /first window already showed the starting picture/i);
  assert.match(relayCaption, /star and leaf choices waited below/i);
  assert.doesNotMatch(relayCaption, /Four empty windows/i);

  assert.match(e03AdultGuide, /five arches alternated over, under, over, under,\s+over/i);
  assert.match(e03AdultGuide, /reverse from an UNDER start/i);
  assert.match(e03AdultGuide, /same two-role rule worked with\s+new names/i);
  assert.deepEqual(e03Book.pages.find(({ page }) => page === 23).sequence, ["over", "under", "over", "question"], "the book keeps its distinct four-position prediction challenge");
  assert.match(e03Book.pages.find(({ page }) => page === 30).text, /STAR · LEAF · STAR · \?/);

  const receipt = JSON.parse(await readFile(new URL("../public/audio/e03-v1.0.0/generation-receipt.json", import.meta.url), "utf8"));
  const manifestBytes = await readFile(new URL("../narration-manifest-e03.json", import.meta.url));
  assert.equal(receipt.manifest_sha256, createHash("sha256").update(manifestBytes).digest("hex"));
  for (const filename of [bridgeLine[0], relayLine[0]]) {
    const recorded = receipt.files.find((entry) => entry.name === `${filename}.mp3`);
    assert.ok(recorded, `${filename} has a generation receipt entry`);
    const audioBytes = await readFile(new URL(`../public/audio/e03-v1.0.0/${filename}.mp3`, import.meta.url));
    assert.equal(recorded.sha256, createHash("sha256").update(audioBytes).digest("hex"));
  }
});

test("Level Three Kokoro narration matches every visible caption and is bundled", async () => {
  assert.equal(levelThreeNarration.lines.length, 32);
  for (const line of levelThreeNarration.lines) {
    const [filename] = line;
    assertCaptionLine(levelThree, line);
    await access(new URL("../public/audio/e03-v1.0.0/" + filename + ".mp3", import.meta.url));
  }
  await access(new URL("../public/audio/e03-v1.0.0/generation-receipt.json", import.meta.url));
  assert.doesNotMatch(levelThree, /\bfetch\s*\(|XMLHttpRequest|WebSocket|sendBeacon/);
});

test("Level Two Kokoro narration matches every visible caption and is bundled", async () => {
  assert.equal(levelTwoNarration.lines.length, 32);
  for (const line of levelTwoNarration.lines) {
    const [filename] = line;
    assertCaptionLine(levelTwo, line);
    await access(new URL("../public/audio/e02-v1.0.0/" + filename + ".mp3", import.meta.url));
  }
  await access(new URL("../public/audio/e02-v1.0.0/generation-receipt.json", import.meta.url));
  assert.doesNotMatch(levelTwo, /\bfetch\s*\(|XMLHttpRequest|WebSocket|sendBeacon/);
});

test("all levels restore locally and background switching stops stale narration", () => {
  assert.match(source, /sft-active-level-v1/);
  assert.match(levelTwo, /sft-e02-moving-stage-v1/);
  assert.match(levelTwo, /localStorage\.setItem\("sft-active-level-v1", "e02"\)/);
  assert.match(levelThree, /localStorage\.setItem\("sft-active-level-v1", "e03"\)/);
  assert.doesNotMatch(levelTwo, /progress\.finished === true \? "select"/);
  assert.doesNotMatch(levelThree, /progress\.finished === true \? "select"/);
  assert.match(levelTwo, /window\.addEventListener\("pagehide", save\)/);
  assert.match(levelTwo, /document\.addEventListener\("visibilitychange", hidden\)/);
  for (const field of ["sceneIndex", "beat", "complete", "finished", "activityStep", "chosen"]) {
    assert.match(levelTwo, new RegExp("\\b" + field + "\\b"));
  }
  for (const component of [source, levelTwo, levelThree]) {
    assert.match(component, /document\.addEventListener\("visibilitychange", stopBackgroundAudio\)/);
    assert.match(component, /window\.addEventListener\("pagehide", stopForPageHide\)/);
    assert.match(component, /document\.visibilityState !== "visible"/);
    assert.match(component, /audioRef\.current = null/);
    assert.match(component, /lessonAudio\?\.pause\(\)/);
  }
});

test("the title offers a confirmed fresh game that clears every level", () => {
  assert.match(source, /Start a fresh game/);
  assert.match(source, /Begin a completely fresh game\?/);
  assert.match(source, /This removes all saved progress from Levels 1, 2 and 3/);
  assert.match(source, /localStorage\.removeItem\(LEVEL_ONE_STORAGE_KEY\)/);
  for (const key of ["sft-e02-moving-stage-v1", "sft-e03-moving-stage-v1"]) {
    assert.match(source, new RegExp(`localStorage\\.removeItem\\(\"${key}\"\\)`));
  }
  assert.match(source, /localStorage\.setItem\("sft-active-level-v1", "select"\)/);
});

test("every finished level explains its lesson directly to the child", () => {
  for (const component of [source, levelTwo, levelThree]) {
    assert.match(component, /NARRATOR TO YOU/);
    assert.match(component, /const endingLesson: Line = \{ speaker: "Narrator"/);
    assert.match(component, /Here is what you learned\./);
    assert.match(component, /This matters because/);
    assert.match(component, /Hear the lesson again/);
  }
});

test("all three levels begin with a four-part narrated prelude", () => {
  assert.match(levelPrelude, /export default function LevelPrelude/);
  assert.match(levelPrelude, /Begin the introduction/);
  assert.match(levelPrelude, /Hear again/);
  assert.match(levelPrelude, /Step into the adventure/);
  assert.match(levelPrelude, /className="prelude-home" onClick=\{onExit\}/);
  assert.match(levelPrelude, /className="prelude-music" onClick=\{onToggleMusic\}/);

  for (const [component, name, lines] of [
    [source, "levelOnePrelude", narration.lines.slice(0, 4)],
    [levelTwo, "levelTwoPrelude", levelTwoNarration.lines.slice(0, 4)],
    [levelThree, "levelThreePrelude", levelThreeNarration.lines.slice(0, 4)],
  ]) {
    assert.match(component, /import LevelPrelude, \{ PreludeLine \} from "\.\/level-prelude"/);
    assert.match(component, new RegExp(`const ${name}: PreludeLine\\[\\] = \\[`));
    assert.match(component, /if \(introOpen\) return <LevelPrelude/);
    assert.ok(component.includes(`lines={${name}}`));
    assert.match(component, /onSpeak=\{\((\w+)\) => \{ startMusic\(\); playLine\(\1\); \}\}/);
    assert.equal(lines.length, 4);
    for (const line of lines) {
      const [, speaker] = line;
      assert.equal(speaker, "Narrator");
      assertCaptionLine(component, line);
    }
  }
  assert.match(levelTwo, /after every game I will explain what your actions helped you learn/);
  assert.match(levelThree, /listen after every game for what you discovered/);
});

test("every playable stage ends with narrator-led teaching", () => {
  for (const [component, count] of [[source, 8], [levelTwo, 9], [levelThree, 9]]) {
    const teachers = [...component.matchAll(/success: \{ speaker: "([^"]+)"/g)].map((match) => match[1]);
    assert.equal(teachers.length, count);
    assert.ok(teachers.every((speaker) => speaker === "Narrator"));
    assert.match(component, /complete \? "NARRATOR · WHAT YOU DISCOVERED" : (?:currentLine|line)\.speaker/);
  }
});

test("three distinct original music tracks are bundled and follow the shared lifecycle", async () => {
  const levelTracks = [
    [source, "level-one"],
    [levelTwo, "level-two"],
    [levelThree, "level-three"],
  ];
  const hashes = new Set();
  for (const [component, track] of levelTracks) {
    assert.ok(component.includes(`useLevelMusic("${track}")`));
    assert.match(component, /onToggleMusic=\{toggleMusic\}/);
    assert.match(component, /Music on/);
    assert.match(component, /Music off/);
    const bytes = await readFile(new URL(`../public/audio/music/${track}.mp3`, import.meta.url));
    assert.ok(bytes.length > 100_000, `${track} contains a full local score`);
    hashes.add(createHash("sha256").update(bytes).digest("hex"));
  }
  assert.equal(hashes.size, 3, "each level has a distinct score");
  assert.match(levelMusic, /new Audio\(`\/audio\/music\/\$\{track\}\.mp3/);
  assert.match(levelMusic, /audio\.loop = true/);
  assert.match(levelMusic, /audio\.preload = "auto"/);
  assert.match(levelMusic, /sft-background-music-v1/);
  assert.match(levelMusic, /document\.visibilityState === "hidden"/);
  assert.match(levelMusic, /document\.addEventListener\("visibilitychange", visibility\)/);
  assert.match(levelMusic, /window\.addEventListener\("pagehide", pageHide\)/);
  assert.match(levelMusic, /audioRef\.current\?\.pause\(\)/);
  assert.match(levelMusic, /audioRef\.current\.currentTime = 0/);
  assert.match(levelMusic, /DUCKED_VOLUME/);
});
