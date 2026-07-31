/** @typedef {"finish" | "transfer-memory"} LevelThreeResolution */

/**
 * A modern save records the prelude milestone directly. For an older save,
 * visible progress is enough evidence that the introduction was completed.
 *
 * @param {Record<string, unknown>} saved
 * @param {boolean} hasStoredProgress
 * @returns {boolean}
 */
export function readLevelThreeIntroSeen(saved, hasStoredProgress) {
  if (typeof saved.introSeen === "boolean") return saved.introSeen;
  if (!hasStoredProgress) return false;
  return saved.finished === true
    || saved.complete === true
    || (typeof saved.sceneIndex === "number" && saved.sceneIndex > 0)
    || (typeof saved.beat === "number" && saved.beat > 0)
    || (typeof saved.activityStep === "number" && saved.activityStep > 0)
    || (Array.isArray(saved.chosen) && saved.chosen.length > 0);
}

/**
 * Keep persisted resolution values inside the two transitions the level knows
 * how to resume. Unknown or older values are ignored safely.
 *
 * @param {unknown} value
 * @returns {LevelThreeResolution | null}
 */
export function readLevelThreeResolution(value) {
  return value === "finish" || value === "transfer-memory" ? value : null;
}

/**
 * Infer a transition from the visible, persisted board as a second line of
 * defence when a page is left immediately after the final correct move.
 *
 * @param {string} activity
 * @param {number[]} chosen
 * @param {number} activityStep
 * @returns {LevelThreeResolution | null}
 */
export function pendingLevelThreeResolution(activity, chosen, activityStep) {
  if (activity === "trail" && chosen.length >= 4) return "finish";
  if (activity === "sides" && chosen.length >= 2) return "finish";
  if (activity === "continue" && chosen.length >= 3) return "finish";
  if (activity === "bridge" && chosen.length >= 5) return "finish";
  if (activity === "routes" && chosen.includes(3)) return "finish";
  if (activity === "transfer" && activityStep === 0 && chosen.length >= 3) return "transfer-memory";
  return null;
}

/**
 * Replay swaps the given role while preserving the same take-turns rule.
 *
 * @param {number} round
 * @returns {{ start: "star" | "leaf", sequence: ["star" | "leaf", "star" | "leaf", "star" | "leaf"] }}
 */
export function levelThreeRelayForRound(round) {
  const start = round % 2 === 0 ? "star" : "leaf";
  const other = start === "star" ? "leaf" : "star";
  return { start, sequence: [other, start, other] };
}
