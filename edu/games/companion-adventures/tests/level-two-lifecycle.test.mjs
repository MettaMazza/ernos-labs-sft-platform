import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  claimLevelTwoCompletion,
  isWinnableParcelRoute,
  LEVEL_TWO_ROUND_VARIANTS,
  levelTwoRoundSetup,
  restoreLevelTwoProgress,
  snapshotLevelTwoProgress,
} from "../app/level-two-state.mjs";

const levelTwo = await readFile(new URL("../app/level-two.tsx", import.meta.url), "utf8");
const levelPrelude = await readFile(new URL("../app/level-prelude.tsx", import.meta.url), "utf8");

const sorted = (values) => [...values].sort((left, right) => left - right);

test("Level Two resumes an exact prelude step and bypasses a completed or legacy prelude", () => {
  assert.deepEqual(restoreLevelTwoProgress(null), {
    schemaVersion: 2,
    introOpen: true,
    preludeStep: -1,
    sceneIndex: 0,
    beat: 0,
    complete: false,
    finished: false,
    activityStep: 0,
    chosen: [],
    mistakes: 0,
    roundLost: false,
    round: 0,
  });

  const inPrelude = restoreLevelTwoProgress(JSON.stringify({
    schemaVersion: 2,
    introOpen: true,
    preludeStep: 2,
    sceneIndex: 0,
  }));
  assert.equal(inPrelude.introOpen, true);
  assert.equal(inPrelude.preludeStep, 2);

  const playing = restoreLevelTwoProgress(JSON.stringify({
    schemaVersion: 2,
    introOpen: false,
    preludeStep: 3,
    sceneIndex: 4,
    beat: 2,
  }));
  assert.equal(playing.introOpen, false);
  assert.equal(playing.preludeStep, 3);
  assert.equal(playing.sceneIndex, 4);
  assert.equal(playing.beat, 2);

  const legacyPlaying = restoreLevelTwoProgress(JSON.stringify({ sceneIndex: 3, beat: 1 }));
  assert.equal(legacyPlaying.introOpen, false);

  for (const terminalSave of [
    { sceneIndex: 0, activityStep: 4, chosen: [11, 6, 7, 2, 3, 4] },
    { sceneIndex: 2, chosen: [2, 4, 1, 3] },
    { sceneIndex: 4, chosen: [3, 1, 4, 2] },
    { sceneIndex: 8, chosen: [4, 2, 3, 1] },
  ]) {
    const recoveredWin = restoreLevelTwoProgress(JSON.stringify({ beat: 2, complete: false, mistakes: 2, ...terminalSave }));
    assert.equal(recoveredWin.complete, true, `scene ${terminalSave.sceneIndex} recovers its earned delayed win`);
    assert.equal(recoveredWin.mistakes, 0);
  }
});

test("Level Two snapshots omit transient feedback and sanitize persisted round state", () => {
  const snapshot = snapshotLevelTwoProgress({
    introOpen: false,
    preludeStep: 3,
    sceneIndex: 99,
    beat: 2.8,
    complete: false,
    finished: false,
    activityStep: 6,
    chosen: [1, 2, "stale", Number.NaN],
    wrong: "This message must not survive a reload.",
    mistakes: 7,
    round: 4.9,
  });

  assert.equal(Object.hasOwn(snapshot, "wrong"), false);
  assert.equal(snapshot.sceneIndex, 8);
  assert.equal(snapshot.beat, 2);
  assert.deepEqual(snapshot.chosen, [1, 2]);
  assert.equal(snapshot.mistakes, 3);
  assert.equal(snapshot.roundLost, true);
  assert.equal(snapshot.round, 4);
});

test("every Level Two replay changes its board while preserving a solution", () => {
  const first = levelTwoRoundSetup(0);
  const second = levelTwoRoundSetup(1);
  for (const field of [
    "parcelRoute",
    "wholeRevealOrder",
    "partCardOrder",
    "match",
    "bridgePieceOrder",
    "count",
    "gap",
    "sumPartOrder",
    "rebuildPieceOrder",
  ]) assert.notDeepEqual(second[field], first[field], `${field} changes on replay`);

  for (const route of LEVEL_TWO_ROUND_VARIANTS.parcelRoutes) assert.equal(isWinnableParcelRoute(route), true);
  for (const order of LEVEL_TWO_ROUND_VARIANTS.wholeRevealOrders) assert.deepEqual(sorted(order), [1, 2, 3, 4]);
  for (const order of LEVEL_TWO_ROUND_VARIANTS.partCardOrders) assert.deepEqual(sorted(order), [1, 2, 3, 4]);
  for (const setup of LEVEL_TWO_ROUND_VARIANTS.matchSetups) {
    assert.deepEqual(sorted(setup.pairOrder), [1, 2]);
    assert.ok(["left", "right"].includes(setup.smallerSide));
  }
  for (const order of LEVEL_TWO_ROUND_VARIANTS.bridgePieceOrders) assert.deepEqual(sorted(order), [1, 2, 3, 4]);
  for (const setup of LEVEL_TWO_ROUND_VARIANTS.countSetups) {
    assert.equal(setup.held.length, 2);
    assert.equal(setup.tray.length, 2);
    assert.deepEqual(sorted([...setup.held, ...setup.tray]), [1, 2, 3, 4]);
  }
  for (const setup of LEVEL_TWO_ROUND_VARIANTS.gapSetups) {
    assert.deepEqual(sorted(setup.pieceOrder), [1, 2, 3]);
    let orientation = setup.initialTurns;
    let reachesUpright = false;
    for (let turn = 0; turn < 4; turn += 1) {
      if (orientation % 4 === 1) reachesUpright = true;
      orientation = (orientation + 1) % 4;
    }
    assert.equal(reachesUpright, true);
  }
  for (const order of LEVEL_TWO_ROUND_VARIANTS.sumPartOrders) assert.deepEqual(sorted(order), [1, 2, 3, 4]);
  for (const order of LEVEL_TWO_ROUND_VARIANTS.rebuildPieceOrders) assert.deepEqual(sorted(order), [1, 2, 3, 4]);
});

test("Level Two completion is synchronous, one-shot and round-resettable", () => {
  const lock = { current: false };
  assert.equal(claimLevelTwoCompletion(lock), true);
  assert.equal(claimLevelTwoCompletion(lock), false);
  lock.current = false;
  assert.equal(claimLevelTwoCompletion(lock), true);

  assert.doesNotMatch(levelTwo, /setTimeout\s*\(\s*finish/);
  assert.match(levelTwo, /if\s*\(!claimLevelTwoCompletion\(completionLockRef\)\) return/);
  assert.match(levelTwo, /setMistakes\(\(value\) => Math\.min\(3, value \+ 1\)\)/);
  assert.match(levelTwo, /className="round-reset"/);
  assert.match(levelTwo, /showFeedback\(/);
  assert.doesNotMatch(levelTwo, /saved\.wrong|setRoundLost/);
});

test("Level Two wires exact prelude progress into the backward-compatible prelude component", () => {
  assert.match(levelPrelude, /initialStep\?: number/);
  assert.match(levelPrelude, /onStepChange\?: \(step: number\) => void/);
  assert.match(levelPrelude, /onStepChange\?\.\(next\)/);
  assert.match(levelTwo, /initialStep=\{preludeStep\}/);
  assert.match(levelTwo, /onStepChange=\{setPreludeStep\}/);
  const snapshotCall = levelTwo.match(/snapshotLevelTwoProgress\(\{([^}]+)\}/s);
  assert.ok(snapshotCall);
  assert.match(snapshotCall[1], /introOpen/);
  assert.match(snapshotCall[1], /preludeStep/);
  assert.doesNotMatch(snapshotCall[1], /wrong/);
});
