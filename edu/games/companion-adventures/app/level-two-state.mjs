const rows = (values) => Object.freeze(values.map((value) => Object.freeze(value)));

export const LEVEL_TWO_STORAGE_KEY = "sft-e02-moving-stage-v1";

export const LEVEL_TWO_ROUND_VARIANTS = Object.freeze({
  parcelRoutes: rows([
    [10, 11, 6, 7, 2, 3, 4],
    [10, 5, 6, 1, 2, 3, 4],
    [10, 11, 12, 7, 8, 3, 4],
  ]),
  wholeRevealOrders: rows([
    [1, 2, 3, 4],
    [3, 1, 4, 2],
    [2, 4, 1, 3],
  ]),
  partCardOrders: rows([
    [2, 4, 1, 3],
    [3, 1, 4, 2],
    [4, 2, 3, 1],
  ]),
  matchSetups: Object.freeze([
    Object.freeze({ pairOrder: Object.freeze([1, 2]), smallerSide: "right" }),
    Object.freeze({ pairOrder: Object.freeze([2, 1]), smallerSide: "left" }),
  ]),
  bridgePieceOrders: rows([
    [3, 1, 4, 2],
    [2, 4, 1, 3],
    [4, 2, 3, 1],
  ]),
  countSetups: Object.freeze([
    Object.freeze({ held: Object.freeze([1, 2]), tray: Object.freeze([3, 4]) }),
    Object.freeze({ held: Object.freeze([2, 1]), tray: Object.freeze([4, 3]) }),
  ]),
  gapSetups: Object.freeze([
    Object.freeze({ pieceOrder: Object.freeze([2, 1, 3]), initialTurns: 0 }),
    Object.freeze({ pieceOrder: Object.freeze([3, 2, 1]), initialTurns: 2 }),
    Object.freeze({ pieceOrder: Object.freeze([1, 3, 2]), initialTurns: 0 }),
  ]),
  sumPartOrders: rows([
    [2, 4, 1, 3],
    [3, 1, 4, 2],
    [4, 2, 3, 1],
  ]),
  rebuildPieceOrders: rows([
    [3, 1, 4, 2],
    [2, 4, 1, 3],
    [4, 2, 3, 1],
  ]),
});

function integerInRange(value, minimum, maximum) {
  if (!Number.isFinite(value)) return minimum;
  return Math.min(maximum, Math.max(minimum, Math.trunc(value)));
}

function variantForRound(variants, round) {
  const safeRound = integerInRange(round, 0, Number.MAX_SAFE_INTEGER);
  return variants[safeRound % variants.length];
}

export function levelTwoRoundSetup(round) {
  return {
    parcelRoute: variantForRound(LEVEL_TWO_ROUND_VARIANTS.parcelRoutes, round),
    wholeRevealOrder: variantForRound(LEVEL_TWO_ROUND_VARIANTS.wholeRevealOrders, round),
    partCardOrder: variantForRound(LEVEL_TWO_ROUND_VARIANTS.partCardOrders, round),
    match: variantForRound(LEVEL_TWO_ROUND_VARIANTS.matchSetups, round),
    bridgePieceOrder: variantForRound(LEVEL_TWO_ROUND_VARIANTS.bridgePieceOrders, round),
    count: variantForRound(LEVEL_TWO_ROUND_VARIANTS.countSetups, round),
    gap: variantForRound(LEVEL_TWO_ROUND_VARIANTS.gapSetups, round),
    sumPartOrder: variantForRound(LEVEL_TWO_ROUND_VARIANTS.sumPartOrders, round),
    rebuildPieceOrder: variantForRound(LEVEL_TWO_ROUND_VARIANTS.rebuildPieceOrders, round),
  };
}

export function isWinnableParcelRoute(route) {
  if (!Array.isArray(route) || route.length < 2 || route[0] !== 10 || route.at(-1) !== 4) return false;
  if (new Set(route).size !== route.length) return false;
  return route.every((cell, index) => {
    if (!Number.isInteger(cell) || cell < 0 || cell > 14) return false;
    if (index === 0) return true;
    const previous = route[index - 1];
    const rowDistance = Math.abs(Math.floor(cell / 5) - Math.floor(previous / 5));
    const columnDistance = Math.abs((cell % 5) - (previous % 5));
    return rowDistance + columnDistance === 1;
  });
}

function defaultProgress() {
  return {
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
  };
}

function normalizedProgress(saved, sceneCount, preludeLineCount, legacySave = false) {
  const introOpen = typeof saved.introOpen === "boolean" ? saved.introOpen : !legacySave;
  const sceneIndex = integerInRange(saved.sceneIndex, 0, Math.max(0, sceneCount - 1));
  const beat = integerInRange(saved.beat, 0, Number.MAX_SAFE_INTEGER);
  const activityStep = integerInRange(saved.activityStep, 0, Number.MAX_SAFE_INTEGER);
  const chosen = Array.isArray(saved.chosen) ? saved.chosen.filter(Number.isInteger) : [];
  const allFourParts = [1, 2, 3, 4].every((part) => chosen.includes(part));
  const legacyTerminalWin = beat >= 2 && ((sceneIndex === 0 && activityStep === 4 && chosen.includes(4))
    || ([2, 4, 8].includes(sceneIndex) && allFourParts));
  const complete = saved.complete === true || legacyTerminalWin;
  const mistakes = complete ? 0 : integerInRange(saved.mistakes, 0, 3);
  return {
    schemaVersion: 2,
    introOpen,
    preludeStep: integerInRange(saved.preludeStep, -1, Math.max(-1, preludeLineCount - 1)),
    sceneIndex,
    beat,
    complete,
    finished: saved.finished === true,
    activityStep,
    chosen,
    mistakes,
    roundLost: mistakes >= 3,
    round: integerInRange(saved.round, 0, Number.MAX_SAFE_INTEGER),
  };
}

export function restoreLevelTwoProgress(raw, sceneCount = 9, preludeLineCount = 4) {
  if (raw == null) return defaultProgress();
  try {
    const saved = typeof raw === "string" ? JSON.parse(raw) : raw;
    if (!saved || typeof saved !== "object" || Array.isArray(saved)) return defaultProgress();
    const legacySave = !Object.hasOwn(saved, "introOpen") && Object.hasOwn(saved, "sceneIndex");
    return normalizedProgress(saved, sceneCount, preludeLineCount, legacySave);
  } catch {
    return defaultProgress();
  }
}

export function snapshotLevelTwoProgress(progress, sceneCount = 9, preludeLineCount = 4) {
  return normalizedProgress({ ...progress, introOpen: progress.introOpen === true }, sceneCount, preludeLineCount);
}

export function claimLevelTwoCompletion(lock) {
  if (lock.current) return false;
  lock.current = true;
  return true;
}
