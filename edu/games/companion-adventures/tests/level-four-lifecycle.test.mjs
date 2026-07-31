import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import {
  LEVEL_FOUR_FINAL_LESSON,
  LEVEL_FOUR_NARRATION,
  LEVEL_FOUR_PICTURES,
  LEVEL_FOUR_SOURCE,
  levelFourRoundForRound,
  nextLevelFourRound,
  pendingLevelFourResolution,
  readLevelFourIntroSeen,
  readLevelFourResolution,
} from "../app/level-four-state.mjs";

const source = await readFile(new URL("../app/level-four.tsx", import.meta.url), "utf8");

function activityBranch(activity) {
  const marker = `if (scene.activity === "${activity}")`;
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, `${activity} needs its own playable branch`);
  const next = source.indexOf('\n    if (scene.activity === "', start + marker.length);
  return source.slice(start, next === -1 ? source.indexOf("\n    return null;", start) : next);
}

const canonicalSource = [
  { symbol: "sun", symbolLabel: "SUN", picture: "sunflower" },
  { symbol: "moon", symbolLabel: "MOON", picture: "bee" },
  { symbol: "leaf", symbolLabel: "LEAF", picture: "watering-can" },
  { symbol: "star", symbolLabel: "STAR", picture: "boot" },
];

const exactLessons = new Map([
  ["01c-narrator-observation", "You moved the lens over the shown plan and found the bee in the moon corner. That was an observation because you used what you could see instead of guessing. A clear observation gives the team a starting record."],
  ["02c-narrator-build-check", "You used every picture once and matched each one to its source corner. Building from a shown source lets the team compare the result with the same starting plan."],
  ["03c-narrator-memory-check", "You studied, covered and rebuilt the four pictures. When the curtain opened, every complete failed rebuild stayed visible. A failed try can still help us check."],
  ["04c-narrator-retained-try", "You compared every corner and found that bee and boot changed places while the other two pictures stayed the same. Comparing the complete source with the complete try is more reliable than one quick guess."],
  ["05c-narrator-trace", "You followed the placement record in order and found Step 3 as the first change. A trace keeps what happened first, next and last, so the team can find where a different result began."],
  ["06c-narrator-boundary", "You aligned the width ribbon and found that the sign fits between the hooks. The ribbon answered width only; it did not check the pictures or height. A measuring tool answers its declared question."],
  ["07c-narrator-independent", "Ivo rebuilt from the same source without seeing the team sign. His four picture places matched, so the fresh check confirmed that result. A separate path matters because copying would not be a fresh check."],
  ["08c-narrator-outcomes", "Mia used the width answer to claim the whole sign fit, but Ivo noticed height was still unchecked. You chose a height tool instead of guessing or voting. Disagreement can show that more work is needed."],
  ["09c-narrator-final-check", "You matched every gate question to its own visible record. The sign passed only after picture, width, height and friend checks were supported. Keeping all the records made the final decision clear."],
]);

const exactFinalLesson = "You learned how to check. You looked at what was shown instead of guessing. You built the sign, covered it, rebuilt it, and kept the first try when it did not match. You followed the steps to find where the change began. You used a width tool for width and a height tool for height, because one tool answers only its own question. Then Ivo checked by a fresh path. His result confirmed the picture places. When Mia and Ivo disagreed, you did more work instead of guessing or voting. Checking matters because it helps us say what we observed, keep useful mistakes, and find the next question that needs an answer.";

test("Level Four has one copy-locked caption for every Kokoro stem", () => {
  assert.equal(LEVEL_FOUR_NARRATION.length, 32);
  const audio = LEVEL_FOUR_NARRATION.map((line) => line.audio);
  assert.equal(new Set(audio).size, audio.length);
  assert.ok(LEVEL_FOUR_NARRATION.every((line) => line.speaker && line.text && !line.text.includes("undefined")));
  assert.equal(LEVEL_FOUR_NARRATION.filter((line) => /^0[1-9]c-/.test(line.audio)).length, 9);

  for (const [stem, expected] of exactLessons) {
    assert.equal(LEVEL_FOUR_NARRATION.find((line) => line.audio === stem)?.text, expected, `${stem} must retain its approved lesson`);
  }
  assert.equal(LEVEL_FOUR_FINAL_LESSON, exactFinalLesson);
  assert.equal(LEVEL_FOUR_NARRATION.at(-1).text, exactFinalLesson);

  assert.match(source, /LEVEL_FOUR_AUDIO_DIRECTORY = "\/audio\/e04-v1\.0\.0"/);
  assert.match(source, /LEVEL_FOUR_MUSIC = "\/audio\/music\/level-four\.mp3"/);
});

test("the handoff reaches a closed gate and introduces Ivo once in the prelude", () => {
  const recap = LEVEL_FOUR_NARRATION.find((line) => line.audio === "00a-narrator-recap")?.text ?? "";
  const mission = LEVEL_FOUR_NARRATION.find((line) => line.audio === "00b-narrator-mission")?.text ?? "";
  const ivoPrelude = LEVEL_FOUR_NARRATION.find((line) => line.audio === "00d-narrator-ivo")?.text ?? "";
  const stageNarration = LEVEL_FOUR_NARRATION.filter((line) => /^0[1-9]/.test(line.audio));

  assert.match(recap, /turning-light trail.*Sunrise Arch/i);
  assert.match(recap, /closed garden gate.*ahead/i);
  assert.match(mission, /beside the closed gate/i);
  assert.doesNotMatch(mission, /beyond|through the gate/i);
  assert.match(ivoPrelude, /met Ivo, the garden checker/i);
  assert.equal(stageNarration.filter((line) => /met Ivo|new friend|Ivo arrives/i.test(line.text)).length, 0, "Ivo is not reintroduced during a stage");

  assert.match(source, /type Character = "mira" \| "tavi" \| "sol" \| "ivo"/);
  assert.match(source, /characters=\{\[[\s\S]*?id:\s*"ivo"[\s\S]*?name:\s*"Ivo"[\s\S]*?image:\s*image\("ivo"\)[\s\S]*?\]\}/);
  assert.doesNotMatch(source, /introduces\??:|introduces:|guest-banner|New friend for Level Four/);
  assert.match(source, /id: "search"[\s\S]*?cast: \["mira", "tavi", "sol", "ivo"\][\s\S]*?activity: "search"/);
  assert.doesNotMatch(source, /\b(?:vee|pax)\b/i);
  assert.match(source, /\/art\/characters\/individual\/ivo\.png/);
  assert.match(source, /\/art\/stages\/e04-stage-01-look-and-point-v2\.png/);
  assert.doesNotMatch(source, /\/art\/stages\/e04-stage-01-look-and-point-v1\.png/);
  assert.equal((source.match(/\/art\/stages\/e04-stage-0[2-9]-[^"']+-v1\.png/g) ?? []).length, 5);
  assert.match(source, /\/art\/stages\/e04-stage-05-placement-record-v2\.png/);
  assert.match(source, /\/art\/stages\/e04-stage-08-height-check-v2\.png/);
  assert.match(source, /\/art\/stages\/e04-stage-09-record-checkpoint-v2\.png/);
});

test("the canonical source law never rotates", () => {
  assert.deepEqual(LEVEL_FOUR_SOURCE, canonicalSource);
  assert.deepEqual(LEVEL_FOUR_PICTURES, canonicalSource.map((entry) => entry.picture));

  for (let round = 0; round < 40; round += 1) {
    const board = levelFourRoundForRound(round);
    assert.deepEqual(board.source, canonicalSource, `round ${round} changed the source law`);
    assert.deepEqual(board.plan, ["sunflower", "bee", "watering-can", "boot"]);
    assert.deepEqual(board.symbols, ["sun", "moon", "leaf", "star"]);
    assert.deepEqual([...board.cardTray].sort(), [...LEVEL_FOUR_PICTURES].sort());
    assert.equal(new Set(board.cardTray).size, 4);
    assert.equal(board.requestPicture, board.plan[board.requestIndex]);
    assert.equal(board.requestSymbol, board.symbols[board.requestIndex]);
    assert.equal(board.requestIndex, 1);
    assert.equal(board.requestSymbol, "moon");
    assert.equal(board.requestPicture, "bee");
    assert.deepEqual(board.memoryPlan, board.plan);
    assert.deepEqual(board.firstTry, ["sunflower", "boot", "watering-can", "bee"]);
    assert.deepEqual(board.differenceIndexes, [1, 3]);
    assert.deepEqual(board.friendBoard, board.plan);
  }
});

test("round zero is deterministic and teaches MOON means BEE first", () => {
  const first = levelFourRoundForRound(0);
  assert.equal(first.variant, 0);
  assert.equal(first.requestIndex, 1);
  assert.equal(first.requestSymbol, "moon");
  assert.equal(first.requestPicture, "bee");
  assert.deepEqual(first.cardTray, ["boot", "watering-can", "bee", "sunflower"]);
  assert.equal(first.firstDepartureIndex, 2, "Step 3 is the first canonical placement departure");
  assert.deepEqual(first.trace.slice(0, 3), [
    { picture: "sunflower", symbol: "sun" },
    { picture: "watering-can", symbol: "leaf" },
    { picture: "boot", symbol: "moon" },
  ]);
  assert.equal(first.measureWidth, 3);
  assert.equal(first.heightTarget, 3);
});

test("all bounded replay variants remain solvable while varying presentation", () => {
  const trays = new Set();
  const traces = new Set();
  const widthTools = new Set();
  const heightTools = new Set();
  const friendPaths = new Set();

  for (let round = 0; round < 40; round += 1) {
    const board = levelFourRoundForRound(round);
    trays.add(board.cardTray.join("|"));
    traces.add(board.trace.map((step) => `${step.picture}:${step.symbol}`).join("|"));
    widthTools.add(board.measureWidth);
    heightTools.add(board.heightTarget);
    friendPaths.add(board.friendOrder.join("|"));

    assert.equal(board.trace.length, 4);
    assert.equal(new Set(board.trace.map((step) => step.picture)).size, 4);
    assert.equal(new Set(board.trace.map((step) => step.symbol)).size, 4);
    const actualDeparture = board.trace.findIndex((step) => canonicalSource.find((entry) => entry.picture === step.picture)?.symbol !== step.symbol);
    assert.equal(board.firstDepartureIndex, actualDeparture);
    assert.equal(actualDeparture, 2, "the copy-locked narrator must truthfully call Step 3 the first change on every replay");
    assert.ok(board.trace.slice(0, actualDeparture).every((step) => canonicalSource.find((entry) => entry.picture === step.picture)?.symbol === step.symbol));

    assert.ok(board.measureWidth >= 2 && board.measureWidth <= 4);
    assert.ok(board.heightTarget >= 2 && board.heightTarget <= 4);
    assert.deepEqual([...board.friendOrder].sort(), ["leaf", "moon", "star", "sun"]);
    assert.deepEqual([...board.checkpointQuestions].sort(), ["friend", "height", "pictures", "width"]);
    assert.deepEqual([...board.checkpointRecords].sort(), ["friend", "height", "pictures", "width"]);
  }

  assert.ok(trays.size > 1, "replays vary the card tray");
  assert.ok(traces.size > 1, "replays vary the safe trace");
  assert.ok(widthTools.size > 1, "replays vary the width tool target");
  assert.ok(heightTools.size > 1, "replays vary the height tool target");
  assert.ok(friendPaths.size > 1, "replays vary Ivo's fresh route");
});

test("replay selection changes family without escaping the four proven variants", () => {
  for (let previous = 0; previous < 4; previous += 1) {
    for (const sample of [0, 0.24, 0.25, 0.5, 0.75, 0.999]) {
      const next = nextLevelFourRound(previous, sample);
      assert.ok(next >= 0 && next < 4);
      assert.notEqual(next, previous);
    }
  }
});

test("restore inference permits only complete guarded one-shot wins", () => {
  assert.equal(pendingLevelFourResolution("search", [], 0), null);
  assert.equal(pendingLevelFourResolution("search", ["bee"], 0), "finish");

  assert.equal(pendingLevelFourResolution("build", ["0:sunflower", "1:bee", "2:watering-can"], 0), null);
  assert.equal(pendingLevelFourResolution("build", ["0:sunflower", "0:bee", "2:watering-can", "3:boot"], 0), null);
  assert.equal(pendingLevelFourResolution("build", ["0:sunflower", "1:bee", "2:watering-can", "3:boot"], 0), "finish");

  assert.equal(pendingLevelFourResolution("memory", ["sunflower", "bee", "watering-can", "boot"], 1), null, "a complete rebuild still needs the explicit whole-board check");
  assert.equal(pendingLevelFourResolution("difference", ["1"], 0), null);
  assert.equal(pendingLevelFourResolution("difference", ["1", "3"], 0), "finish");
  assert.equal(pendingLevelFourResolution("trace", ["0", "1", "2", "3"], 0), null);
  assert.equal(pendingLevelFourResolution("measure", [], 4), null);
  assert.equal(pendingLevelFourResolution("friend", ["sun:sunflower", "moon:bee", "leaf:watering-can", "star:boot"], 4), null, "Ivo's board still needs an explicit comparison");
  assert.equal(pendingLevelFourResolution("height", ["height"], 4), null);

  assert.equal(pendingLevelFourResolution("checkpoint", ["pictures:pictures", "width:width", "height:height"], 0), null);
  assert.equal(pendingLevelFourResolution("checkpoint", ["pictures:pictures", "pictures:width", "height:height", "friend:friend"], 0), null);
  assert.equal(pendingLevelFourResolution("checkpoint", ["pictures:pictures", "width:width", "height:height", "friend:friend"], 0), "finish");
});

test("modern and legacy saves restore the prelude and one-shot resolution safely", () => {
  assert.equal(readLevelFourIntroSeen({}, false), false);
  assert.equal(readLevelFourIntroSeen({ introSeen: false, sceneIndex: 7 }, true), false);
  assert.equal(readLevelFourIntroSeen({ introSeen: true }, true), true);
  assert.equal(readLevelFourIntroSeen({ sceneIndex: 1 }, true), true);
  assert.equal(readLevelFourIntroSeen({ beat: 1 }, true), true);
  assert.equal(readLevelFourIntroSeen({ finished: true }, true), true);
  assert.equal(readLevelFourResolution("finish"), "finish");
  assert.equal(readLevelFourResolution("old-transition"), null);
  assert.equal(readLevelFourResolution(null), null);
});

test("nine distinct games teach the complete checking sequence", () => {
  const activities = ["search", "build", "memory", "difference", "trace", "measure", "friend", "height", "checkpoint"];
  const branches = Object.fromEntries(activities.map((activity) => [activity, activityBranch(activity)]));
  assert.equal((source.match(/id: "[^"]+", title: "[^"]+", gameTitle:/g) ?? []).length, 9);

  assert.match(branches.search, /SHOWN SOURCE/);
  assert.match(branches.search, /lens/i);
  assert.match(branches.search, /requestPicture/);
  assert.match(branches.search, /config\.cardTray\.map/, "the child chooses the observed picture instead of the lens auto-answering");

  assert.match(branches.build, /config\.source\.map/);
  assert.match(branches.build, /config\.cardTray\.map/);
  assert.match(branches.build, /onDragStart/);
  assert.match(branches.build, /onClick/);

  assert.match(branches.memory, /chosen\.length !== 4/);
  assert.match(branches.memory, /chosen\.every/);
  assert.match(branches.memory, /setMemoryAttempts/);
  assert.match(branches.memory, /memoryAttempts\.map/);
  assert.doesNotMatch(branches.memory, /setMemoryAttempts\(\[\]\)/, "Look again must not erase retained complete tries");

  assert.match(branches.difference, /differenceIndexes/);
  assert.match(branches.difference, /next\.length === 2/);
  assert.match(branches.difference, /COMPLETE SOURCE/);
  assert.match(branches.difference, /COMPLETE FIRST REBUILD/);

  assert.match(branches.trace, /STEP \{index \+ 1\}/);
  assert.match(branches.trace, /index !== expectedIndex/);
  assert.match(branches.trace, /first, next and last/i);
  assert.doesNotMatch(branches.trace, /e04-dpad|followLevelFourRoute/, "the placement trace is not the removed shed route game");

  assert.match(branches.measure, /LEFT HOOK/);
  assert.match(branches.measure, /RIGHT HOOK/);
  assert.match(branches.measure, /HEIGHT NOT CHECKED/);
  assert.match(branches.measure, /measureWidth/);

  assert.match(branches.friend, /config\.friendOrder/);
  assert.match(branches.friend, /config\.source/);
  assert.match(branches.friend, /TEAM SIGN/);
  assert.match(branches.friend, /TEAM ANSWER HIDDEN/);
  assert.match(branches.friend, /selected === "uncovered"/);
  assert.match(branches.friend, /chosen\.length < 4/);
  assert.match(branches.friend, /CONFIRM/);
  assert.doesNotMatch(branches.friend, /TAVI(?:&apos;|')S COPY|Slide Tavi/i);

  assert.match(branches.height, /CHECK HEIGHT/);
  assert.match(branches.height, /GUESS/);
  assert.match(branches.height, /VOTE/);
  assert.match(branches.height, /heightTarget/);
  assert.match(branches.height, /BOTTOM/);
  assert.match(branches.height, /TOP/);

  assert.match(branches.checkpoint, /checkpointQuestions/);
  assert.match(branches.checkpoint, /checkpointRecords/);
  assert.match(branches.checkpoint, /PICTURES/);
  assert.match(branches.checkpoint, /WIDTH/);
  assert.match(branches.checkpoint, /HEIGHT/);
  assert.match(branches.checkpoint, /FRIEND CHECK/);

  assert.match(source, /const next = mistakes \+ 1/);
  assert.match(source, /if \(next >= 3\) setRoundLost\(true\)/);
  assert.match(source, /failed tr(?:y|ies).*still|KEPT COMPLETE TRIES/is);
  assert.match(source, /Try a new board/);
  assert.match(source, /setTried\(\(values\)/);
});

test("all nine exact book codes are available and no prototype code remains", () => {
  const block = source.match(/const bookCodes: Record<string, string> = \{([\s\S]*?)\n\};/)?.[1] ?? "";
  const codes = [...block.matchAll(/^\s+([A-Z]+):/gm)].map((match) => match[1]);
  assert.deepEqual(codes, [
    "LOOKCLOSE",
    "SIGNMAKER",
    "KEEPFIRST",
    "SPOTCHANGE",
    "FOLLOWSTEPS",
    "WIDTHONLY",
    "FRIENDCHECK",
    "MOREWORK",
    "ALLCHECKED",
  ]);
});

test("fresh play is round zero while replays vary, and exact visible progress resumes", () => {
  assert.match(source, /setRound\(typeof saved\.round === "number" \? Math\.max\(0, saved\.round\) : 0\)/);
  assert.match(source, /catch \{\s*setRound\(0\)/);
  assert.match(source, /function retryRound\(\) \{[\s\S]*nextLevelFourRound\(round\)/);
  assert.match(source, /function replay\(\) \{[\s\S]*nextLevelFourRound\(round\)/);
  assert.match(source, /function restart\(\) \{[\s\S]*resetActivity\(0\)/);
  assert.match(source, /sft-e04-garden-check-v1/);
  assert.match(source, /progressRef\.current = \{[^}]*memoryAttempts[^}]*resolution[^}]*\}/);
  assert.match(source, /setMemoryAttempts\(Array\.isArray\(saved\.memoryAttempts\)/);
});

test("app switching stops narration and cannot schedule an old line twice", () => {
  assert.match(source, /document\.addEventListener\("visibilitychange", hide\)/);
  assert.match(source, /window\.addEventListener\("pagehide", pageHide\)/);
  assert.match(source, /stopNarration\(audioRef, narrationGenerationRef, duckMusic\)/);
  assert.match(source, /lastLineRef\.current === key/);
  assert.match(source, /narrationGenerationRef\.current !== generation/);
  assert.match(source, /endingLessonPlayedRef/);
  assert.match(source, /if \(document\.visibilityState !== "visible"/);
});

test("the ending opens the gate only after all four records and explains the lesson", () => {
  assert.match(source, /The garden gate opens\./);
  assert.match(source, /source comparison/i);
  assert.match(source, /width record/i);
  assert.match(source, /height record/i);
  assert.match(source, /Ivo(?:'|’|&apos;)s fresh (?:friend-)?check record/i);
  assert.equal((source.match(/The garden gate opens\./g) ?? []).length, 1, "the gate opens at the ending, not during an earlier stage");
});
