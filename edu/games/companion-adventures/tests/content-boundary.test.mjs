import assert from "node:assert/strict";
import { access, readFile } from "node:fs/promises";
import test from "node:test";

const source = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
const levelTwo = await readFile(new URL("../app/level-two.tsx", import.meta.url), "utf8");
const levelThree = await readFile(new URL("../app/level-three.tsx", import.meta.url), "utf8");
const styles = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
const gameplayStandard = await readFile(new URL("../GAMEPLAY_STANDARD.md", import.meta.url), "utf8");
const manifest = JSON.parse(await readFile(new URL("../game-manifest.json", import.meta.url), "utf8"));
const claimMap = JSON.parse(await readFile(new URL("../claim-map.json", import.meta.url), "utf8"));
const narration = JSON.parse(await readFile(new URL("../narration-manifest.json", import.meta.url), "utf8"));
const continuity = JSON.parse(await readFile(new URL("../character-continuity.json", import.meta.url), "utf8"));
const e02Book = JSON.parse(await readFile(new URL("../../../books/E02-one-whole-many-parts/source/book-v1.0.0.json", import.meta.url), "utf8"));
const e03Book = JSON.parse(await readFile(new URL("../../../books/E03-the-fold-makes-a-pattern/source/book-v1.0.0.json", import.meta.url), "utf8"));
const e03ClaimMap = JSON.parse(await readFile(new URL("../../../books/E03-the-fold-makes-a-pattern/claim-map.json", import.meta.url), "utf8"));

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
  assert.match(source, /className="emoji-prop recall-box/);
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
  assert.match(levelTwo, /className="ending-home" onClick=\{onExit\}/);
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
    "The Star Door was shut", "A note came through the letter box",
    "Mia picked up the note and opened it", "My brown teddy is inside",
    "Tap the toy to lift it out. Then tap the box", "The first star turned gold. A blue door opened",
    "The friends went through the door", "I found a white card on this table",
    "seven wall tiles lit up, one after another", "My teddy rolled out of my bag",
    "Now all five stars were gold, and the Star Door opened", "Mia folded the note",
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
  assert.equal(narration.lines.length, 36);
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
  assert.equal((levelTwo.match(/id: "/g) ?? []).length, 9);
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
  assert.match(levelTwo, /4 COUNTED PARTS → 1 WHOLE LANTERN/);
  assert.match(levelTwo, /The equation checked all four parts/);
  assert.match(levelTwo, /That balanced match is called symmetrical/);
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
    "All four lantern parts went through the small door. Each part moved once",
    "the same whole lantern is back",
    "All four lantern parts were still separate",
  ]) assert.ok(levelTwo.includes(phrase));
  assert.doesNotMatch(levelTwo, /next door|next room|first door opens|last door opens/i);
  assert.doesNotMatch(levelTwo, /great brass|brass rectangular|magical door|registered|partition|fitted tray|coordinate|gold seal|door woke/i);
});

test("Book Two keeps four parts separate until addition and the one final rebuild", () => {
  const page = (number) => e02Book.pages.find((entry) => entry.page === number);
  assert.match(page(16).subtext, /Matching sides around the middle are called symmetrical/);
  assert.match(page(23).text, /flat practice frame/);
  assert.match(page(24).subtext, /returned all four parts to the carrying tray/);
  assert.match(page(26).text, /four separate parts to the balcony/);
  assert.match(page(28).text, /1 PART \+ 1 PART \+ 1 PART \+ 1 PART = \? PARTS/);
  assert.match(page(29).text, /EQUALS sign says both sides count the same four parts/);
  assert.doesNotMatch(e02Book.pages.filter((entry) => entry.page < 30).map((entry) => entry.text).join(" "), /same Moon Lantern was ONE WHOLE again/);
  assert.match(page(30).text, /same Moon Lantern was ONE WHOLE again/);
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

test("Level Three Kokoro narration matches every visible caption and is bundled", async () => {
  const levelThreeNarration = JSON.parse(await readFile(new URL("../narration-manifest-e03.json", import.meta.url), "utf8"));
  assert.equal(levelThreeNarration.lines.length, 28);
  for (const [filename, speaker, caption] of levelThreeNarration.lines) {
    assert.match(levelThree, new RegExp('audio: "' + filename + '"'));
    assert.ok(levelThree.includes('speaker: "' + speaker + '", text: "' + caption.replaceAll('"', '\\"') + '"'));
    await access(new URL("../public/audio/e03-v1.0.0/" + filename + ".mp3", import.meta.url));
  }
  await access(new URL("../public/audio/e03-v1.0.0/generation-receipt.json", import.meta.url));
  assert.doesNotMatch(levelThree, /\bfetch\s*\(|XMLHttpRequest|WebSocket|sendBeacon/);
});

test("Level Two Kokoro narration matches every visible caption and is bundled", async () => {
  const levelTwoNarration = JSON.parse(await readFile(new URL("../narration-manifest-e02.json", import.meta.url), "utf8"));
  assert.equal(levelTwoNarration.lines.length, 28);
  for (const [filename, speaker, caption] of levelTwoNarration.lines) {
    assert.match(levelTwo, new RegExp('audio: "' + filename + '"'));
    assert.ok(levelTwo.includes('speaker: "' + speaker + '", text: "' + caption.replaceAll('"', '\\"') + '"'));
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
  for (const key of ["sft-e01-moving-stage-v1", "sft-e02-moving-stage-v1", "sft-e03-moving-stage-v1"]) {
    assert.match(source, new RegExp(`localStorage\\.removeItem\\(\"${key}\"\\)`));
  }
  assert.match(source, /localStorage\.setItem\("sft-active-level-v1", "select"\)/);
});

test("every finished level explains its lesson directly to the child", () => {
  for (const component of [source, levelTwo, levelThree]) {
    assert.match(component, /NARRATOR TO YOU/);
    assert.match(component, /Here is the lesson\./);
    assert.match(component, /This matters because/);
  }
});
