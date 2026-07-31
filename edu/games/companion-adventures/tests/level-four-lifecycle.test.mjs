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
const styles = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");
const narrationManifest = JSON.parse(await readFile(new URL("../narration-manifest-e04.json", import.meta.url), "utf8"));

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

const exactFinalLesson = "Here is what you learned. You looked at the picture plan instead of guessing. You kept Sol's wrong sign and compared it with the plan. You followed Sol's moves and found the first move that changed. You measured side to side for width, then bottom to top for height. Ivo made a new sign without looking at the team's sign, and both signs matched. When Mia and Ivo were not sure, you checked again. At the gate, you put each of the four answer cards beside the question it answered. This matters because a careful check helps us find mistakes, shows what we know, and tells us what still needs checking.";

test("Level Four has one copy-locked caption for every Kokoro stem", () => {
  assert.equal(LEVEL_FOUR_NARRATION.length, 32);
  const audio = LEVEL_FOUR_NARRATION.map((line) => line.audio);
  assert.equal(new Set(audio).size, audio.length);
  assert.ok(LEVEL_FOUR_NARRATION.every((line) => line.speaker && line.text && !line.text.includes("undefined")));
  assert.equal(LEVEL_FOUR_NARRATION.filter((line) => /^0[1-9]c-/.test(line.audio)).length, 9);

  const runtimeTriples = LEVEL_FOUR_NARRATION.map(({ audio: stem, speaker, text }) => [stem, speaker, text]);
  assert.deepEqual(runtimeTriples, narrationManifest.lines, "the manifest, visible captions and Kokoro stems must stay exactly copy-locked");
  assert.equal(LEVEL_FOUR_FINAL_LESSON, exactFinalLesson);
  assert.equal(LEVEL_FOUR_NARRATION.at(-1).text, exactFinalLesson);
  assert.match(LEVEL_FOUR_NARRATION.find((line) => line.audio === "01c-narrator-observation")?.text ?? "", /find by looking is called an observation/i);
  assert.match(LEVEL_FOUR_NARRATION.find((line) => line.audio === "04c-narrator-retained-try")?.text ?? "", /called comparing/i);
  assert.match(LEVEL_FOUR_NARRATION.find((line) => line.audio === "05c-narrator-trace")?.text ?? "", /record is something we keep to remember what happened/i);
  assert.match(LEVEL_FOUR_NARRATION.find((line) => line.audio === "07c-narrator-independent")?.text ?? "", /without seeing or copying.*called an independent check/i);
  assert.match(LEVEL_FOUR_NARRATION.find((line) => line.audio === "09c-narrator-final-check")?.text ?? "", /Evidence is something we can point to that shows what we found/i);

  assert.match(source, /LEVEL_FOUR_AUDIO_DIRECTORY = "\/audio\/e04-v1\.0\.1"/);
  assert.match(source, /LEVEL_FOUR_MUSIC = "\/audio\/music\/level-four\.mp3"/);
});

test("the handoff reaches a closed gate and introduces Ivo once in the prelude", () => {
  const recap = LEVEL_FOUR_NARRATION.find((line) => line.audio === "00a-narrator-recap")?.text ?? "";
  const mission = LEVEL_FOUR_NARRATION.find((line) => line.audio === "00b-narrator-mission")?.text ?? "";
  const ivoPrelude = LEVEL_FOUR_NARRATION.find((line) => line.audio === "00d-narrator-ivo")?.text ?? "";
  const stageNarration = LEVEL_FOUR_NARRATION.filter((line) => /^0[1-9]/.test(line.audio));

  assert.match(recap, /moon-and-sun light.*Sunrise Arch.*closed garden gate/i);
  assert.match(mission, /Welcome Sign.*before the morning visitors arrive.*picture plan and an empty sign/i);
  assert.doesNotMatch(mission, /beyond|through the gate/i);
  assert.match(ivoPrelude, /garden helper called Ivo.*look twice.*without peeking/i);
  assert.equal(stageNarration.filter((line) => /met Ivo|meet Ivo|new friend|Ivo arrives|called Ivo/i.test(line.text)).length, 0, "Ivo is introduced once in the prelude, not introduced again during a stage");

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
  assert.equal(first.heightTarget, 4, "the visible full-height tool is the answer");
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
    assert.equal(board.heightTarget, 4, `round ${round} must keep the visible top edge at height 4`);
    assert.deepEqual([...board.friendOrder].sort(), ["leaf", "moon", "star", "sun"]);
    assert.deepEqual([...board.checkpointQuestions].sort(), ["friend", "height", "pictures", "width"]);
    assert.deepEqual([...board.checkpointRecords].sort(), ["friend", "height", "pictures", "width"]);
  }

  assert.ok(trays.size > 1, "replays vary the card tray");
  assert.ok(traces.size > 1, "replays vary the safe trace");
  assert.ok(widthTools.size > 1, "replays vary the width tool target");
  assert.deepEqual([...heightTools], [4], "replays must not hide a different answer behind the same full-height picture");
  assert.ok(friendPaths.size > 1, "replays vary Ivo's fresh route");
});

test("both measuring activities are unlimited learning practice instead of try-light traps", () => {
  const measure = activityBranch("measure");
  const height = activityBranch("height");
  const learningTryStart = source.indexOf("function learningTry(");
  const resetStart = source.indexOf("function resetActivity(", learningTryStart);
  const learningTry = source.slice(learningTryStart, resetStart);

  assert.notEqual(learningTryStart, -1, "measurement feedback needs a non-consuming learningTry helper");
  assert.match(learningTry, /setTried\(/, "learning attempts remain visible");
  assert.match(learningTry, /setWrong\(/, "learning attempts explain what to adjust");
  assert.doesNotMatch(learningTry, /setMistakes\(|setRoundLost\(|wrongTry\(/, "learning attempts must not consume or darken try lights");

  assert.match(measure, /learningTry\([^;]+`measure:\$\{widthValue\}`\)/s, "short and long width calibrations are non-consuming");
  assert.doesNotMatch(measure, /wrongTry\(/, "width calibration cannot end the round");

  assert.match(height, /choice !== "height"[\s\S]*?learningTry\([\s\S]*?`height-choice:\$\{choice\}`\)/, "guess and vote are non-consuming teaching choices");
  assert.match(height, /learningTry\([^;]+`height:\$\{heightValue\}`\)/s, "short and long height calibrations are non-consuming");
  assert.doesNotMatch(height, /wrongTry\(/, "height exploration cannot end the round");

  assert.match(source, /scene\.activity === "measure" \|\| scene\.activity === "height"[\s\S]*?e04-practice-badge[\s\S]*?TRY AS MANY LENGTHS AS YOU NEED[\s\S]*?: <TryLights mistakes=\{mistakes\}/, "both measuring scenes replace try lights with an explicit unlimited-practice badge");
  assert.match(styles, /\.e04-practice-badge\s*\{/, "the unlimited-practice message is visibly styled");
});

test("the visible width and height boundaries agree with every accepted answer", () => {
  const measure = activityBranch("measure");
  const height = activityBranch("height");

  assert.match(measure, /e04-gate-frame width-\$\{config\.measureWidth\}/, "the gate geometry is keyed to the round's accepted width");
  assert.match(measure, /e04-ribbon width-\$\{widthValue\}/, "the visible ribbon follows the child's selected width");
  for (const target of [2, 3, 4]) {
    assert.match(styles, new RegExp(`\\.e04-gate-frame\\.width-${target} \\.e04-ribbon\\.width-${target}\\{width:100%\\}`), `width ${target} visibly touches both hooks when accepted`);
  }

  assert.match(height, /heightValue !== config\.heightTarget/);
  assert.match(height, /e04-height-tool height-\$\{heightValue\}/, "the visible height tool follows the child's selected height");
  assert.match(styles, /\.e04-height-tool\.height-1\{height:25%\}\.e04-height-tool\.height-2\{height:50%\}\.e04-height-tool\.height-3\{height:75%\}\.e04-height-tool\.height-4\{height:100%\}/, "only height 4 reaches the visible top edge");

  for (let round = 0; round < 40; round += 1) {
    assert.equal(levelFourRoundForRound(round).heightTarget, 4, `round ${round} accepts the one tool that visibly reaches the top`);
  }
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

  assert.match(branches.search, /PICTURE PLAN/);
  assert.doesNotMatch(branches.search, /SHOWN SOURCE/, "the child's named object is a picture plan, not rejected source jargon");
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
  assert.match(branches.difference, /PICTURE PLAN/);
  assert.match(branches.difference, /SOL(?:&apos;|')S FIRST SIGN/);

  assert.match(branches.trace, /MOVE \{index \+ 1\}/);
  assert.match(branches.trace, /index !== expectedIndex/);
  assert.match(branches.trace, /FIRST MOVE THAT CHANGED/);
  assert.doesNotMatch(branches.trace, /e04-dpad|followLevelFourRoute/, "the placement trace is not the removed shed route game");

  assert.match(branches.measure, /LEFT HOOK/);
  assert.match(branches.measure, /RIGHT HOOK/);
  assert.match(branches.measure, /HEIGHT NOT CHECKED/);
  assert.match(branches.measure, /measureWidth/);

  assert.match(branches.friend, /config\.friendOrder/);
  assert.match(branches.friend, /config\.source/);
  assert.match(branches.friend, /OUR SIGN/);
  assert.match(branches.friend, /OUR SIGN IS HIDDEN/);
  assert.match(branches.friend, /selected === "uncovered"/);
  assert.match(branches.friend, /chosen\.length < 4/);
  assert.match(branches.friend, /Do the two signs match\?/);
  assert.doesNotMatch(branches.friend, /TAVI(?:&apos;|')S COPY|Slide Tavi/i);

  assert.match(branches.height, /USE A HEIGHT TOOL/);
  assert.match(branches.height, /GUESS/);
  assert.match(branches.height, /VOTE/);
  assert.match(branches.height, /heightTarget/);
  assert.match(branches.height, /BOTTOM/);
  assert.match(branches.height, /TOP/);

  assert.match(branches.checkpoint, /checkpointQuestions/);
  assert.match(branches.checkpoint, /checkpointRecords/);
  assert.match(branches.checkpoint, /FOUR ANSWER CARDS/);
  assert.match(branches.checkpoint, /FOUR GATE QUESTIONS/);
  assert.match(branches.checkpoint, /All four pictures match the plan/);
  assert.match(branches.checkpoint, /The ribbon touched both side hooks/);
  assert.match(branches.checkpoint, /The tool touched the bottom and top/);
  assert.match(branches.checkpoint, /Ivo(?:&apos;|')s sign matched ours/);

  assert.match(source, /const next = mistakes \+ 1/);
  assert.match(source, /if \(next >= 3\) setRoundLost\(true\)/);
  assert.match(branches.memory, /This sign does not match the picture plan yet\. It will stay below so you can see your try/i);
  assert.match(branches.memory, /MY EARLIER SIGNS/);
  assert.match(source, /Try a new puzzle/);
  assert.match(source, /setTried\(\(values\)/);
});

test("the physical garden story repairs the sign before measuring and welcomes the waiting visitors", () => {
  const traceLesson = LEVEL_FOUR_NARRATION.find((line) => line.audio === "05c-narrator-trace")?.text ?? "";
  const openingMission = LEVEL_FOUR_NARRATION.find((line) => line.audio === "00b-narrator-mission")?.text ?? "";
  const finalCheckpoint = LEVEL_FOUR_NARRATION.find((line) => line.audio === "09a-narrator-checkpoint")?.text ?? "";
  const traceScene = source.indexOf('id: "trace"');
  const measureScene = source.indexOf('id: "measure"');
  const checkpointScene = source.indexOf('id: "checkpoint"');

  assert.ok(traceScene >= 0 && traceScene < measureScene && measureScene < checkpointScene, "repair, measuring and the final gate check stay in physical story order");
  assert.match(traceLesson, /Mia puts the bee and boot back in their right corners\. Now the sign matches/i, "Stage 5 visibly repairs Sol's sign");
  assert.match(source.slice(measureScene, checkpointScene), /Mia has fixed the two mixed-up pictures\. She lifts the sign towards two hooks on the gate/i, "the repaired sign, rather than an unexplained new object, reaches measuring");

  assert.match(openingMission, /before the morning visitors arrive/i, "the opening establishes who is waiting for the sign");
  assert.match(source.slice(checkpointScene), /morning visitors wait beyond the gate/i, "Stage 9 brings the opening visitors back before the gate opens");
  assert.match(finalCheckpoint, /Four empty locks.*One answer card waits for each question/i, "four physical cards answer four visible gate locks");
  assert.match(source.slice(checkpointScene), /FOUR ANSWER CARDS[\s\S]*?config\.checkpointRecords\.map/, "the child can see and move all four answer cards");
  assert.match(source.slice(checkpointScene), /gate opened for the morning visitors/i, "the ending resolves the opening need");
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

test("the ending opens the gate only after four concrete checks and explains the lesson simply", () => {
  assert.match(source, /The garden gate opens\./);
  assert.match(source, /Its pictures matched the plan\./i);
  assert.match(source, /width ribbon touched both side hooks/i);
  assert.match(source, /height tool touched the bottom and top edges/i);
  assert.match(source, /Ivo(?:'|’|&apos;)s sign matched too/i);
  assert.match(source, /One check answers one question\. Four questions needed four checks\./);
  assert.equal(LEVEL_FOUR_FINAL_LESSON, exactFinalLesson);
  assert.doesNotMatch(LEVEL_FOUR_FINAL_LESSON, /declared question|supported|fresh path|finite counts|outcomes/i, "the final lesson keeps the accepted child-first wording instead of rejected jargon");
  assert.equal((source.match(/The garden gate opens\./g) ?? []).length, 1, "the gate opens at the ending, not during an earlier stage");
});
