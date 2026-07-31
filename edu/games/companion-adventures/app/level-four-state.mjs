/** @typedef {"finish"} LevelFourResolution */

/**
 * Copy-locked visible captions and their Kokoro file stems. Any change here
 * requires the E04 narration manifest and local audio to be regenerated.
 */
export const LEVEL_FOUR_NARRATION = Object.freeze([
  { audio: "00a-narrator-recap", speaker: "Narrator", heading: "The light reaches the arch", text: "You repaired the turning-light trail and helped its light reach the Sunrise Arch. The closed garden gate waited just ahead." },
  { audio: "00b-narrator-mission", speaker: "Narrator", heading: "One sign beside the gate", text: "Beside the closed gate stood a four-picture source plan and a blank Garden Welcome Sign. The sign had to be rebuilt and checked before the morning visitors arrived." },
  { audio: "00c-narrator-discover", speaker: "Narrator", heading: "What you will discover", text: "You will look at a source, build and rebuild, keep a failed try, follow its steps, measure one named question at a time, and use four records at the final checkpoint." },
  { audio: "00d-narrator-ivo", speaker: "Narrator", heading: "Meet Ivo", text: "At the closed gate, Mia, Sol and Tavi met Ivo, the garden checker. He was moss-green and carried a round magnifying lens in his hand and a checkerboard satchel across his body. He joined the team to check the sign by a fresh path." },

  { audio: "01a-narrator-gate", speaker: "Narrator", text: "The source plan beside the closed gate had four named corners: sun, moon, leaf and star. Each corner held one picture." },
  { audio: "01b-mia-find", speaker: "Mia", text: "The first question asks, Which picture is at moon? Move the lens over the shown plan. Then use the lens to choose what you can really see in the moon corner." },
  { audio: "01c-narrator-observation", speaker: "Narrator", text: "You moved the lens over the shown plan and found the bee in the moon corner. That was an observation because you used what you could see instead of guessing. A clear observation gives the team a starting record." },

  { audio: "02a-narrator-ivo-arrives", speaker: "Narrator", text: "The source stayed beside the gate. The four blank sign corners carried the same sun, moon, leaf and star marks." },
  { audio: "02b-ivo-build", speaker: "Ivo", text: "Use every picture once. Drag a card, or tap it and then tap its matching symbol corner. Keep the source visible while you build." },
  { audio: "02c-narrator-build-check", speaker: "Narrator", text: "You used every picture once and matched each one to its source corner. Building from a shown source lets the team compare the result with the same starting plan." },

  { audio: "03a-narrator-curtain", speaker: "Narrator", text: "The team studied the complete source. Then the curtain covered it, and a fresh four-corner rebuild board waited." },
  { audio: "03b-tavi-memory", speaker: "Tavi", text: "Use all four cards once to make a complete rebuild. When it is complete, check the whole board. If it does not match, keep that exact try and look again." },
  { audio: "03c-narrator-memory-check", speaker: "Narrator", text: "You studied, covered and rebuilt the four pictures. When the curtain opened, every complete failed rebuild stayed visible. A failed try can still help us check." },

  { audio: "04a-narrator-first-try", speaker: "Narrator", text: "Sol's complete first rebuild stayed beside the complete source. Bee and boot had traded places, while sunflower and watering can stayed where they began." },
  { audio: "04b-sol-compare", speaker: "Sol", text: "Compare every symbol corner. Mark both corners that changed. If a corner matches, mark it checked and keep looking." },
  { audio: "04c-narrator-retained-try", speaker: "Narrator", text: "You compared every corner and found that bee and boot changed places while the other two pictures stayed the same. Comparing the complete source with the complete try is more reliable than one quick guess." },

  { audio: "05a-narrator-footprints", speaker: "Narrator", text: "Sol kept four placement cards showing what he did first, next and last. The cards made an ordered record of his rebuild." },
  { audio: "05b-mia-trace", speaker: "Mia", text: "Start with Step 1 and check the cards in order against the source. Stop when you reach the first step that placed a picture in a different corner." },
  { audio: "05c-narrator-trace", speaker: "Narrator", text: "You followed the placement record in order and found Step 3 as the first change. A trace keeps what happened first, next and last, so the team can find where a different result began." },

  { audio: "06a-narrator-frame", speaker: "Narrator", text: "The repaired picture places were recorded. The next card asked only whether the sign's width fitted between the two gate hooks." },
  { audio: "06b-ivo-measure", speaker: "Ivo", text: "Align the width ribbon from the left hook to the right hook. This tool checks width only. It does not check the pictures or the sign's height." },
  { audio: "06c-narrator-boundary", speaker: "Narrator", text: "You aligned the width ribbon and found that the sign fits between the hooks. The ribbon answered width only; it did not check the pictures or height. A measuring tool answers its declared question." },

  { audio: "07a-narrator-friend-check", speaker: "Narrator", text: "The team sign was hidden behind a screen. Ivo took the same source, fresh cards and a separate work board so he could not copy the team's answer." },
  { audio: "07b-tavi-scan", speaker: "Ivo", text: "Guide my lens through the source corners in the order shown. Record each source picture on my fresh board. We will uncover the team sign only after my four places are complete." },
  { audio: "07c-narrator-independent", speaker: "Narrator", text: "Ivo rebuilt from the same source without seeing the team sign. His four picture places matched, so the fresh check confirmed that result. A separate path matters because copying would not be a fresh check." },

  { audio: "08a-narrator-disagreement", speaker: "Narrator", text: "The width record passed. Mia said the whole sign fitted, but Ivo noticed that nobody had checked its height from the bottom edge to the top edge." },
  { audio: "08b-ivo-outcomes", speaker: "Ivo", text: "Do not guess and do not vote. Choose the missing height question, then move the height tool from the bottom edge to the top edge and test the fit." },
  { audio: "08c-narrator-outcomes", speaker: "Narrator", text: "Mia used the width answer to claim the whole sign fit, but Ivo noticed height was still unchecked. You chose a height tool instead of guessing or voting. Disagreement can show that more work is needed." },

  { audio: "09a-narrator-checkpoint", speaker: "Narrator", text: "The closed gate asked four questions: pictures, width, height and friend check. Four visible records waited to be matched to the question each one had answered." },
  { audio: "09b-mia-final", speaker: "Mia", text: "Choose one record, then match it to its gate question. A wrong match will stay on the checking rail. The gate must wait until all four questions have support." },
  { audio: "09c-narrator-final-check", speaker: "Narrator", text: "You matched every gate question to its own visible record. The sign passed only after picture, width, height and friend checks were supported. Keeping all the records made the final decision clear." },

  { audio: "10-narrator-to-you", speaker: "Narrator", text: "You learned how to check. You looked at what was shown instead of guessing. You built the sign, covered it, rebuilt it, and kept the first try when it did not match. You followed the steps to find where the change began. You used a width tool for width and a height tool for height, because one tool answers only its own question. Then Ivo checked by a fresh path. His result confirmed the picture places. When Mia and Ivo disagreed, you did more work instead of guessing or voting. Checking matters because it helps us say what we observed, keep useful mistakes, and find the next question that needs an answer." },
]);

export const LEVEL_FOUR_SOURCE = Object.freeze([
  Object.freeze({ symbol: "sun", symbolLabel: "SUN", picture: "sunflower" }),
  Object.freeze({ symbol: "moon", symbolLabel: "MOON", picture: "bee" }),
  Object.freeze({ symbol: "leaf", symbolLabel: "LEAF", picture: "watering-can" }),
  Object.freeze({ symbol: "star", symbolLabel: "STAR", picture: "boot" }),
]);

export const LEVEL_FOUR_PICTURES = Object.freeze(LEVEL_FOUR_SOURCE.map((entry) => entry.picture));
export const LEVEL_FOUR_PICTURE_LABELS = Object.freeze({
  sunflower: "sunflower",
  bee: "bee",
  "watering-can": "watering can",
  boot: "boot",
});

export const LEVEL_FOUR_FINAL_LESSON = LEVEL_FOUR_NARRATION.at(-1).text;

const TRACE_VARIANTS = Object.freeze([
  Object.freeze([
    { picture: "sunflower", symbol: "sun" },
    { picture: "watering-can", symbol: "leaf" },
    { picture: "boot", symbol: "moon" },
    { picture: "bee", symbol: "star" },
  ]),
  Object.freeze([
    { picture: "sunflower", symbol: "sun" },
    { picture: "bee", symbol: "moon" },
    { picture: "boot", symbol: "leaf" },
    { picture: "watering-can", symbol: "star" },
  ]),
  Object.freeze([
    { picture: "watering-can", symbol: "leaf" },
    { picture: "boot", symbol: "star" },
    { picture: "bee", symbol: "sun" },
    { picture: "sunflower", symbol: "moon" },
  ]),
  Object.freeze([
    { picture: "boot", symbol: "star" },
    { picture: "bee", symbol: "moon" },
    { picture: "watering-can", symbol: "sun" },
    { picture: "sunflower", symbol: "leaf" },
  ]),
]);

const FRIEND_ORDERS = Object.freeze([
  ["moon", "star", "sun", "leaf"],
  ["leaf", "sun", "star", "moon"],
  ["star", "leaf", "moon", "sun"],
  ["sun", "moon", "leaf", "star"],
]);

const RECORDS = Object.freeze(["pictures", "width", "height", "friend"]);

function positiveModulo(value, divisor) {
  return ((value % divisor) + divisor) % divisor;
}

function rotate(values, places) {
  const offset = positiveModulo(places, values.length);
  return [...values.slice(offset), ...values.slice(0, offset)];
}

function firstTraceDeparture(trace) {
  return trace.findIndex((step) => LEVEL_FOUR_SOURCE.find((entry) => entry.picture === step.picture)?.symbol !== step.symbol);
}

/** @param {number} previous @param {number} sample */
export function nextLevelFourRound(previous = -1, sample = Math.random()) {
  const bounded = Number.isFinite(sample) ? Math.min(Math.max(sample, 0), 0.999999) : 0;
  const candidate = Math.floor(bounded * 4);
  return candidate === positiveModulo(previous, 4) ? (candidate + 1) % 4 : candidate;
}

/**
 * The source law and the narrated opening question never vary. Card trays,
 * trace presentation, tool targets and record presentation vary between
 * proven-solvable rounds.
 *
 * @param {number} round
 */
export function levelFourRoundForRound(round) {
  const variant = positiveModulo(Math.trunc(round) || 0, 4);
  const source = LEVEL_FOUR_SOURCE.map((entry) => ({ ...entry }));
  const plan = source.map((entry) => entry.picture);
  const symbols = source.map((entry) => entry.symbol);
  const cardTray = rotate([...plan].reverse(), variant);
  // Mia's caption and its Kokoro clip always ask for MOON and name BEE.
  const requestIndex = 1;
  const firstTry = ["sunflower", "boot", "watering-can", "bee"];
  const trace = TRACE_VARIANTS[variant].map((entry) => ({ ...entry }));
  const firstDepartureIndex = firstTraceDeparture(trace);

  return {
    variant,
    source,
    plan,
    symbols,
    cardTray,
    requestIndex,
    requestSymbol: symbols[requestIndex],
    requestPicture: plan[requestIndex],
    memoryPlan: [...plan],
    firstTry,
    differenceIndexes: [1, 3],
    trace,
    firstDepartureIndex,
    measureWidth: [3, 2, 4, 3][variant],
    friendOrder: [...FRIEND_ORDERS[variant]],
    friendBoard: [...plan],
    heightTarget: [3, 2, 4, 3][variant],
    checkpointQuestions: [...RECORDS],
    checkpointRecords: rotate([...RECORDS], variant + 1),
  };
}

/** @param {Record<string, unknown>} saved @param {boolean} hasStoredProgress */
export function readLevelFourIntroSeen(saved, hasStoredProgress) {
  if (typeof saved.introSeen === "boolean") return saved.introSeen;
  if (!hasStoredProgress) return false;
  return saved.finished === true
    || saved.complete === true
    || (typeof saved.sceneIndex === "number" && saved.sceneIndex > 0)
    || (typeof saved.beat === "number" && saved.beat > 0)
    || (Array.isArray(saved.chosen) && saved.chosen.length > 0);
}

/** @param {unknown} value @returns {LevelFourResolution | null} */
export function readLevelFourResolution(value) {
  return value === "finish" ? value : null;
}

/**
 * Restore-only inference. Answer-specific activities finish in their guarded
 * input event so a final correct action cannot win twice.
 *
 * @param {string} activity
 * @param {string[]} chosen
 * @returns {LevelFourResolution | null}
 */
export function pendingLevelFourResolution(activity, chosen) {
  if (activity === "search" && chosen.length >= 1) return "finish";
  if (activity === "build" && new Set(chosen.map((value) => value.split(":")[0])).size >= 4) return "finish";
  if (activity === "difference" && new Set(chosen).size >= 2) return "finish";
  if (activity === "checkpoint" && new Set(chosen.map((value) => value.split(":")[0])).size >= 4) return "finish";
  return null;
}
