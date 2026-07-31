export const LEVEL_ONE_STORAGE_KEY = "sft-e01-moving-stage-v1";

export const LEVEL_ONE_ACTIVITIES = [
  "note",
  "box",
  "bell",
  "card",
  "word",
  "curtain",
  "doors",
  "recall",
];

const LEVEL_ONE_ROUND_VARIANTS = [
  {
    noteOrder: ["map", "book", "note"],
    doorOrder: ["A", "B"],
    recallOrder: ["box", "toy"],
  },
  {
    noteOrder: ["book", "note", "map"],
    doorOrder: ["B", "A"],
    recallOrder: ["toy", "box"],
  },
  {
    noteOrder: ["note", "map", "book"],
    doorOrder: ["A", "B"],
    recallOrder: ["toy", "box"],
  },
];

function clampInteger(value, minimum, maximum, fallback = minimum) {
  const number = Number(value);
  if (!Number.isFinite(number)) return fallback;
  return Math.min(maximum, Math.max(minimum, Math.trunc(number)));
}

function validCardInk(value) {
  if (typeof value !== "string") return "";
  if (!value.startsWith("data:image/png;base64,") || value.length > 250_000) return "";
  return value;
}

export function levelOneRoundSetup(round = 0) {
  const safeRound = clampInteger(round, 0, Number.MAX_SAFE_INTEGER, 0);
  const variant = LEVEL_ONE_ROUND_VARIANTS[safeRound % LEVEL_ONE_ROUND_VARIANTS.length];
  return {
    noteOrder: [...variant.noteOrder],
    doorOrder: [...variant.doorOrder],
    recallOrder: [...variant.recallOrder],
  };
}

export function pendingLevelOneResolution(activity, state = {}) {
  if (state.resolution === "finish") return "finish";
  if (activity === "word" && clampInteger(state.letters, 0, 7, 0) >= 7) return "finish";
  if (
    activity === "curtain" &&
    (clampInteger(state.curtain, 0, 100, 0) >= 100 ||
      clampInteger(state.activityStep, 0, 20, 0) >= 1)
  ) {
    return "finish";
  }
  if (activity === "doors") {
    const doors = Array.isArray(state.doors) ? state.doors : [];
    if (doors.includes("A") && doors.includes("B")) return "finish";
  }
  return null;
}

function hasLegacyGameplay(saved, sceneIndex, beat, activityStep, stars, doors) {
  return Boolean(
    saved.finished ||
      saved.complete ||
      saved.resolution === "finish" ||
      sceneIndex > 0 ||
      beat > 0 ||
      activityStep > 0 ||
      stars > 0 ||
      clampInteger(saved.letters, 0, 7, 0) > 0 ||
      clampInteger(saved.curtain, 0, 100, 0) > 0 ||
      doors.length > 0 ||
      saved.drawn ||
      saved.cardOpen
  );
}

export function restoreLevelOneProgress(raw, sceneCount = LEVEL_ONE_ACTIVITIES.length, preludeCount = 4) {
  let saved = {};
  if (typeof raw === "string" && raw.trim()) {
    try {
      saved = JSON.parse(raw);
    } catch {
      saved = {};
    }
  } else if (raw && typeof raw === "object") {
    saved = raw;
  }

  const lastScene = Math.max(0, sceneCount - 1);
  const sceneIndex = clampInteger(saved.sceneIndex, 0, lastScene, 0);
  const beat = clampInteger(saved.beat, 0, 100, 0);
  let activityStep = clampInteger(saved.activityStep, 0, 20, 0);
  const stars = clampInteger(saved.stars, 0, 5, 0);
  const doors = Array.isArray(saved.doors)
    ? [...new Set(saved.doors.filter((door) => door === "A" || door === "B"))]
    : [];
  const activity = LEVEL_ONE_ACTIVITIES[sceneIndex] ?? LEVEL_ONE_ACTIVITIES[0];
  const storedResolution = saved.resolution === "finish" ? "finish" : null;
  const recoveredWin = pendingLevelOneResolution(activity, {
    resolution: storedResolution,
    letters: saved.letters,
    curtain: saved.curtain,
    activityStep,
    doors,
  });
  const complete = saved.complete === true || recoveredWin === "finish";

  // Old Level One saves used activityStep for temporary wrong-answer messages and
  // for a pointer that might no longer be held. Those states must not reappear.
  if (!complete && (activity === "note" || activity === "bell" || activity === "recall")) {
    activityStep = 0;
  }

  const legacyGameplay = hasLegacyGameplay(saved, sceneIndex, beat, activityStep, stars, doors);
  const finished = saved.finished === true;
  const introOpen = finished
    ? false
    : typeof saved.introOpen === "boolean"
      ? saved.introOpen
      : !legacyGameplay;

  return {
    schemaVersion: 2,
    started: saved.started === true,
    introOpen,
    preludeStep: clampInteger(saved.preludeStep, -1, Math.max(-1, preludeCount - 1), -1),
    sceneIndex,
    beat,
    activityStep,
    complete,
    finished,
    stars,
    letters: clampInteger(saved.letters, 0, 7, 0),
    curtain: clampInteger(saved.curtain, 0, 100, 0),
    doors,
    drawn: saved.drawn === true,
    cardOpen: saved.cardOpen === true,
    cardInk: validCardInk(saved.cardInk),
    round: clampInteger(saved.round, 0, Number.MAX_SAFE_INTEGER, 0),
    resolution: complete ? null : storedResolution,
  };
}

export function snapshotLevelOneProgress(progress, sceneCount, preludeCount) {
  return restoreLevelOneProgress(progress, sceneCount, preludeCount);
}

export function claimLevelOneCompletion(lock) {
  if (lock.current) return false;
  lock.current = true;
  return true;
}
