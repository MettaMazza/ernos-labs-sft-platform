import assert from "node:assert/strict";
import test from "node:test";
import { startNarration, stopNarration } from "../app/narration-controller.mjs";

class FakeAudio {
  constructor(src) {
    this.src = src;
    this.paused = true;
    this.loaded = 0;
    this.listeners = new Map();
  }
  addEventListener(name, listener) { this.listeners.set(name, listener); }
  play() { this.paused = false; return Promise.resolve(); }
  pause() { this.paused = true; }
  removeAttribute(name) { if (name === "src") this.src = ""; }
  load() { this.loaded += 1; }
  emit(name) { this.listeners.get(name)?.(); }
}

function controllerState() {
  const ducks = [];
  return {
    audioRef: { current: null },
    generationRef: { current: 0 },
    ducks,
    duckMusic: (value) => ducks.push(value),
  };
}

test("hidden pages never start narration", () => {
  const state = controllerState();
  const audio = startNarration({
    src: "old-line.mp3",
    ...state,
    AudioConstructor: FakeAudio,
    visibility: () => "hidden",
  });
  assert.equal(audio, null);
  assert.equal(state.audioRef.current, null);
  assert.deepEqual(state.ducks, []);
});

test("stopping narration invalidates, pauses and resets the current clip", async () => {
  const state = controllerState();
  const audio = startNarration({
    src: "line-a.mp3",
    ...state,
    AudioConstructor: FakeAudio,
    visibility: () => "visible",
  });
  await Promise.resolve();
  assert.equal(audio.paused, false);
  const playingGeneration = state.generationRef.current;
  stopNarration(state.audioRef, state.generationRef, state.duckMusic);
  assert.equal(state.generationRef.current, playingGeneration + 1);
  assert.equal(state.audioRef.current, null);
  assert.equal(audio.paused, true);
  assert.equal(audio.src, "");
  assert.equal(audio.loaded, 1);
  assert.equal(state.ducks.at(-1), false);
});

test("a delayed mobile play promise cannot revive a clip after app switching", async () => {
  let resolvePlay;
  class DelayedAudio extends FakeAudio {
    play() {
      this.paused = false;
      return new Promise((resolve) => { resolvePlay = resolve; });
    }
  }
  const state = controllerState();
  const audio = startNarration({
    src: "frozen-line.mp3",
    ...state,
    AudioConstructor: DelayedAudio,
    visibility: () => "visible",
  });
  stopNarration(state.audioRef, state.generationRef, state.duckMusic);
  resolvePlay();
  await Promise.resolve();
  await Promise.resolve();
  assert.equal(audio.paused, true);
  assert.equal(audio.src, "");
  assert.equal(state.audioRef.current, null);
});

test("an old clip ending cannot unduck or replace the newer line", async () => {
  const state = controllerState();
  const first = startNarration({ src: "line-a.mp3", ...state, AudioConstructor: FakeAudio, visibility: () => "visible" });
  const second = startNarration({ src: "line-b.mp3", ...state, AudioConstructor: FakeAudio, visibility: () => "visible" });
  await Promise.resolve();
  first.emit("ended");
  assert.equal(state.audioRef.current, second);
  assert.equal(state.ducks.at(-1), true);
  second.emit("ended");
  assert.equal(state.audioRef.current, null);
  assert.equal(state.ducks.at(-1), false);
});
