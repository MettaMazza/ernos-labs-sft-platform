import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

import {
  claimLevelOneCompletion,
  levelOneRoundSetup,
  restoreLevelOneProgress,
  snapshotLevelOneProgress,
} from "../app/level-one-state.mjs";

const levelOne = await readFile(new URL("../app/page.tsx", import.meta.url), "utf8");
const styles = await readFile(new URL("../app/globals.css", import.meta.url), "utf8");

test("Level One resumes its exact prelude, scene and ending, including legacy five-star saves", () => {
  const fresh = restoreLevelOneProgress(null);
  assert.equal(fresh.introOpen, true);
  assert.equal(fresh.preludeStep, -1);
  assert.equal(fresh.sceneIndex, 0);

  const inPrelude = restoreLevelOneProgress({ introOpen: true, preludeStep: 2, sceneIndex: 0 });
  assert.equal(inPrelude.introOpen, true);
  assert.equal(inPrelude.preludeStep, 2);

  const playing = restoreLevelOneProgress({ introOpen: false, preludeStep: 3, sceneIndex: 4, beat: 1, letters: 3, round: 2 });
  assert.equal(playing.introOpen, false);
  assert.equal(playing.sceneIndex, 4);
  assert.equal(playing.beat, 1);
  assert.equal(playing.letters, 3);
  assert.equal(playing.round, 2);

  const legacyFiveStars = restoreLevelOneProgress({ started: false, sceneIndex: 7, stars: 5, beat: 2 });
  assert.equal(legacyFiveStars.introOpen, false);
  assert.equal(legacyFiveStars.sceneIndex, 7);

  const ending = restoreLevelOneProgress({ started: false, introOpen: false, sceneIndex: 7, stars: 5, finished: true });
  assert.equal(ending.finished, true);
  assert.equal(ending.introOpen, false);
});

test("Level One recovers wins that were suspended before their delayed reveal completed", () => {
  for (const terminalSave of [
    { sceneIndex: 4, letters: 7 },
    { sceneIndex: 5, curtain: 100, activityStep: 1 },
    { sceneIndex: 6, doors: ["A", "B"] },
    { sceneIndex: 0, resolution: "finish" },
  ]) {
    const restored = restoreLevelOneProgress({ introOpen: false, complete: false, ...terminalSave });
    assert.equal(restored.complete, true, `scene ${terminalSave.sceneIndex} recovers its earned win`);
    assert.equal(restored.resolution, null);
  }
});

test("Level One snapshots keep durable play state and discard temporary feedback", () => {
  const snapshot = snapshotLevelOneProgress({
    introOpen: false,
    preludeStep: 3,
    sceneIndex: 99,
    beat: 2.9,
    stars: 12,
    doors: ["A", "A", "stale", "B"],
    cardInk: "not-an-image",
    round: 4.8,
    feedback: "Do not restore me",
    earnedStar: 5,
  });
  assert.equal(snapshot.sceneIndex, 7);
  assert.equal(snapshot.beat, 2);
  assert.equal(snapshot.stars, 5);
  assert.deepEqual(snapshot.doors, ["A", "B"]);
  assert.equal(snapshot.cardInk, "");
  assert.equal(snapshot.round, 4);
  assert.equal(Object.hasOwn(snapshot, "feedback"), false);
  assert.equal(Object.hasOwn(snapshot, "earnedStar"), false);
});

test("Level One completion is one-shot, locked while resolving and visibly resettable", () => {
  const lock = { current: false };
  assert.equal(claimLevelOneCompletion(lock), true);
  assert.equal(claimLevelOneCompletion(lock), false);
  lock.current = false;
  assert.equal(claimLevelOneCompletion(lock), true);

  assert.match(levelOne, /if \(!claimLevelOneCompletion\(completionLockRef\)\) return/);
  assert.match(levelOne, /className="resolution-lock" disabled=\{resolving\}/);
  assert.match(levelOne, /className="round-reset"/);
  assert.doesNotMatch(levelOne, /window\.setTimeout\(finishActivity/);
  assert.match(levelOne, /function beginLevelOne\(\) \{\s*setStarted\(true\)/);
  assert.doesNotMatch(levelOne, /function beginLevelOne\(\)[\s\S]{0,100}setIntroOpen\(true\)/);
});

test("Level One replay variants remain complete and its desktop prelude cast clears the copy panel", () => {
  const first = levelOneRoundSetup(0);
  const second = levelOneRoundSetup(1);
  assert.notDeepEqual(first.noteOrder, second.noteOrder);
  assert.notDeepEqual(first.doorOrder, second.doorOrder);
  assert.notDeepEqual(first.recallOrder, second.recallOrder);
  assert.deepEqual([...second.noteOrder].sort(), ["book", "map", "note"]);
  assert.deepEqual([...second.doorOrder].sort(), ["A", "B"]);
  assert.deepEqual([...second.recallOrder].sort(), ["box", "toy"]);

  assert.match(levelOne, /initialStep=\{preludeStep\}/);
  assert.match(levelOne, /onStepChange=\{setPreludeStep\}/);
  assert.match(styles, /\.prelude-cast \{[^}]*right:1\.5%;[^}]*width:39%;/);
  assert.match(styles, /\.prelude-cast,\.level-one-prelude \.prelude-cast \{ top:5%; left:4%; right:4%; width:auto;/);
});
